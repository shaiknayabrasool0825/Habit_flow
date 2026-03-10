from flask import Blueprint, request, jsonify, send_file, flash
from flask_login import login_required, current_user
from models import db, Habit, HabitLog, Suggestion, WeeklyReport, Session, calculate_habit_streak
from datetime import datetime, timedelta
from gamification import check_achievements
from smart_coach import analyze_user_habits, generate_weekly_report, get_week_feedback
from report_generator import generate_daily_report, generate_weekly_report as gen_weekly_pdf, generate_monthly_report
from utils import can_recover_habit, update_habit_schedule

api_bp = Blueprint('api', __name__)

@api_bp.route('/next-action')
@login_required
def get_next_action_route():
    from decision_engine import get_next_action
    result = get_next_action(current_user.id)
    return jsonify(result)

@api_bp.route('/habit/<int:habit_id>/risk-score', methods=['GET'])
@login_required
def get_habit_risk_score(habit_id):
    """
    Returns the failure probability for the given habit in the next 24-48 hours.
    Requires authentication over current context.
    """
    from ml_logic import predict_failure_probability
    habit = Habit.query.get_or_404(habit_id)
    
    if habit.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    failure_risk = predict_failure_probability(current_user.id, habit.id)
    
    # Categorize Risk Level
    if failure_risk < 0.3:
        risk_level = "Low"
    elif failure_risk < 0.6:
        risk_level = "Medium"
    else:
        risk_level = "High"
        
    return jsonify({
        "failure_risk": round(failure_risk, 2),
        "risk_level": risk_level
    })

@api_bp.route('/session/start/<int:habit_id>', methods=['POST'])
@login_required
def start_session(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    duration = 25 # Default 25 minutes
    
    session_obj = Session(
        user_id=current_user.id,
        habit_id=habit.id,
        planned_duration=duration,
        status='active'
    )
    db.session.add(session_obj)
    db.session.commit()
        
    return jsonify({
        "status": "started", 
        "session_id": session_obj.id,
        "duration": duration
    })

@api_bp.route('/session/finish/<int:session_id>', methods=['POST'])
@login_required
def finish_session(session_id):
    session_obj = Session.query.get_or_404(session_id)
    if session_obj.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    if session_obj.status != 'active':
        return jsonify({"error": "Session is not active"}), 400
        
    session_obj.status = 'completed'
    session_obj.end_time = datetime.utcnow()
    
    today = datetime.utcnow().date()
    existing_log = HabitLog.query.filter_by(habit_id=session_obj.habit_id, date=today).first()
    
    if not existing_log:
        xp_gain = 10
        new_log = HabitLog(
            habit_id=session_obj.habit_id, 
            date=today, 
            status=True, 
            completion_type='completed',
            xp_earned=xp_gain,
            created_at=datetime.utcnow()
        )
        db.session.add(new_log)
        current_user.xp = (current_user.xp if current_user.xp else 0) + xp_gain
        db.session.commit()
        
        # Update streak/achievements
        from gamification import check_achievements
        check_achievements(current_user)
        
    db.session.commit()
    return jsonify({"success": True})

@api_bp.route('/session/cancel/<int:session_id>', methods=['POST'])
@login_required
def cancel_session(session_id):
    session_obj = Session.query.get_or_404(session_id)
    if session_obj.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    session_obj.status = 'cancelled'
    session_obj.end_time = datetime.utcnow()
    db.session.commit()
    
    return jsonify({"success": True})

@api_bp.route('/session/reflection/<int:session_id>', methods=['POST'])
@login_required
def session_reflection(session_id):
    session_obj = Session.query.get_or_404(session_id)
    if session_obj.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    reflection = data.get('reflection')
    
    if reflection in ['Energizing', 'Neutral', 'Difficult', 'Avoided']:
        session_obj.reflection = reflection
        db.session.commit()
        return jsonify({"success": True})
        
    return jsonify({"error": "Invalid reflection type"}), 400


@api_bp.route('/log_habit/<int:habit_id>')
@login_required
def log_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    today = datetime.utcnow().date()
    existing_log = HabitLog.query.filter_by(habit_id=habit.id, date=today).first()
    
    response_data = {
        'success': True,
        'xp_gained': 0,
        'badges_unlocked': [],
        'new_xp': current_user.xp,
        'new_level': (current_user.xp // 100) + 1,
        'status': 'completed' if not existing_log else 'unchecked'
    }

    if existing_log:
        xp_to_remove = existing_log.xp_earned if existing_log.xp_earned is not None else 10
        db.session.delete(existing_log)
        if current_user.xp:
             current_user.xp = max(0, current_user.xp - xp_to_remove)
             response_data['xp_gained'] = -xp_to_remove
        response_data['new_xp'] = current_user.xp
        db.session.commit()
    else:
        xp_gain = 10
        new_log = HabitLog(
            habit_id=habit.id, 
            date=today, 
            status=True, 
            completion_type='completed',
            xp_earned=xp_gain,
            created_at=datetime.utcnow()
        )
        db.session.add(new_log)
        current_user.xp = (current_user.xp if current_user.xp else 0) + xp_gain
        response_data['xp_gained'] = xp_gain
        db.session.commit()
        
        new_achievements = check_achievements(current_user)
        ach_list = []
        for ach in new_achievements:
            ach_list.append({
                'name': ach.name,
                'description': ach.description,
                'icon': ach.icon,
                'xp': ach.xp_reward
            })
        response_data['achievements_unlocked'] = ach_list
        response_data['new_xp'] = current_user.xp
        
    db.session.commit()
    return jsonify(response_data)

@api_bp.route('/suggestions')
@login_required
def get_coach_suggestions():
    analyze_user_habits(current_user.id)
    suggestions = Suggestion.query.filter_by(
        user_id=current_user.id, 
        is_dismissed=False
    ).order_by(Suggestion.created_at.desc()).all()
    
    return jsonify({
        "suggestions": [{
            "id": s.id,
            "habit_name": s.habit.name,
            "type": s.type,
            "message": s.message,
            "suggested_value": s.suggested_value
        } for s in suggestions]
    })

@api_bp.route('/suggestions/<int:suggestion_id>/dismiss', methods=['POST'])
@login_required
def dismiss_suggestion(suggestion_id):
    suggestion = Suggestion.query.get_or_404(suggestion_id)
    if suggestion.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    suggestion.is_dismissed = True
    db.session.commit()
    return jsonify({"success": True})

@api_bp.route('/suggestions/<int:suggestion_id>/accept', methods=['POST'])
@login_required
def accept_suggestion(suggestion_id):
    suggestion = Suggestion.query.get_or_404(suggestion_id)
    if suggestion.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    habit = Habit.query.get(suggestion.habit_id)
    if not habit:
        return jsonify({"error": "Habit not found"}), 404
        
    if suggestion.type == 'time_change':
        try:
            from datetime import datetime
            new_time = datetime.strptime(suggestion.suggested_value, '%H:%M:%S').time()
            habit.start_time = new_time
            # Update end time to start + 30 mins
            from datetime import timedelta
            end_dt = datetime.combine(datetime.today(), new_time) + timedelta(minutes=30)
            habit.end_time = end_dt.time()
        except Exception as e:
            return jsonify({"error": f"Failed to apply time change: {str(e)}"}), 500
    elif suggestion.type == 'frequency_reduction':
        habit.frequency = suggestion.suggested_value
        
    suggestion.is_dismissed = True
    db.session.commit()
    return jsonify({"success": True})

@api_bp.route('/weekly-report')
@login_required
def get_weekly_report():
    one_week_ago = datetime.utcnow() - timedelta(days=6)
    report = WeeklyReport.query.filter(
        WeeklyReport.user_id == current_user.id,
        WeeklyReport.created_at >= one_week_ago
    ).order_by(WeeklyReport.created_at.desc()).first()
    
    if not report:
        report = generate_weekly_report(current_user.id)
        
    if not report:
        return jsonify({"report": None})
        
    return jsonify({
        "report": {
            "week_start": report.week_start_date.strftime('%Y-%m-%d'),
            "week_end": report.week_end_date.strftime('%Y-%m-%d'),
            "completion_rate": report.completion_rate,
            "best_day": report.best_day,
            "worst_day": report.worst_day,
            "strongest_habit": report.strongest_habit.name if report.strongest_habit else "None",
            "weakest_habit": report.weakest_habit.name if report.weakest_habit else "None",
            "suggestion": report.suggestion_text,
            "best_day_rate": report.best_day_rate,
            "worst_day_rate": report.worst_day_rate,
            "total_checkins": report.total_checkins,
            "prev_week_diff": report.prev_week_diff,
            "next_week_plan": report.next_week_plan.split('\n') if report.next_week_plan else [],
            "feedback": get_week_feedback(report.completion_rate),
            "xp_awarded": report.xp_bonus_awarded
        }
    })

@api_bp.route('/weekly-report/apply-plan', methods=['POST'])
@login_required
def apply_weekly_plan():
    # Simple implementation: grant a small "planning" bonus
    current_user.xp = (current_user.xp or 0) + 15
    db.session.commit()
    return jsonify({"success": True, "xp_gained": 15, "new_xp": current_user.xp})

@api_bp.route('/download/daily')
@login_required
def download_daily():
    path = generate_daily_report(current_user.id)
    if path:
        return send_file(path, as_attachment=True)
    return "Not enough data for daily report", 400

@api_bp.route('/download/weekly')
@login_required
def download_weekly():
    path = gen_weekly_pdf(current_user.id)
    if path:
        return send_file(path, as_attachment=True)
    return "Not enough data for weekly report", 400

@api_bp.route('/download/monthly')
@login_required
def download_monthly():
    path = generate_monthly_report(current_user.id)
    if path:
        return send_file(path, as_attachment=True)
    return "Not enough data for monthly report", 400

@api_bp.route('/export/data')
@login_required
def export_data():
    from flask import jsonify
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    data = []
    for h in habits:
        logs_data = [{'date': l.date.strftime('%Y-%m-%d'), 'status': l.status, 'type': l.completion_type, 'xp': l.xp_earned} for l in h.logs]
        data.append({
            'name': h.name,
            'frequency': h.frequency,
            'color': h.color,
            'icon': h.icon,
            'start_time': h.start_time.strftime('%H:%M:%S') if h.start_time else None,
            'logs': logs_data
        })
    return jsonify({"user": current_user.username, "habits": data})

@api_bp.route('/habits/<int:habit_id>/recover', methods=['POST'])
@login_required
def recover_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    if not can_recover_habit(habit, current_user):
        return jsonify({"error": "Recovery not available"}), 400
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    new_log = HabitLog(
        habit_id=habit.id,
        date=yesterday,
        status=True,
        completion_type='recovered',
        xp_earned=0,
        created_at=datetime.utcnow()
    )
    db.session.add(new_log)
    current_user.last_recovery_date = datetime.utcnow().date()
    db.session.commit()
    return jsonify({"success": True, "new_streak": calculate_habit_streak(habit.id, current_user.id)})

@api_bp.route('/habits/<int:habit_id>/late', methods=['POST'])
@login_required
def late_checkin(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    today = datetime.utcnow().date()
    if HabitLog.query.filter_by(habit_id=habit.id, date=today).first():
        return jsonify({"error": "Already completed today"}), 400
    xp = 7
    new_log = HabitLog(
        habit_id=habit.id, date=today, status=True,
        completion_type='late', xp_earned=xp, created_at=datetime.utcnow()
    )
    db.session.add(new_log)
    current_user.xp = (current_user.xp or 0) + xp
    db.session.commit()
    return jsonify({"success": True, "xp_gained": xp, "new_xp": current_user.xp})

@api_bp.route('/habits/<int:habit_id>/partial', methods=['POST'])
@login_required
def partial_checkin(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    today = datetime.utcnow().date()
    if HabitLog.query.filter_by(habit_id=habit.id, date=today).first():
        return jsonify({"error": "Already completed today"}), 400
    xp = 5
    new_log = HabitLog(
        habit_id=habit.id, date=today, status=True,
        completion_type='partial', xp_earned=xp, created_at=datetime.utcnow()
    )
    db.session.add(new_log)
    current_user.xp = (current_user.xp or 0) + xp
    db.session.commit()
    return jsonify({"success": True, "xp_gained": xp, "new_xp": current_user.xp})

@api_bp.route('/habits/<int:habit_id>/reschedule', methods=['POST'])
@login_required
def reschedule_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json() or request.form
    new_time_str = data.get('new_time')
    if not new_time_str:
         return jsonify({"error": "Missing new_time"}), 400
    try:
        new_start = datetime.strptime(new_time_str, '%H:%M').time()
        update_habit_schedule(habit, new_start)
        db.session.commit()
        return jsonify({"success": True})
    except ValueError:
        return jsonify({"error": "Invalid time format"}), 400
