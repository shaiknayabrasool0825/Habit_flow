from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, User, Habit, HabitLog, calculate_habit_streak
from ml_logic import (
    predict_completion_probability, 
    calculate_impact_analysis, 
    get_suggestions, 
    recommend_best_time, 
    get_risky_habits, 
    get_productivity_window
)
from smart_coach import analyze_user_habits
from utils import can_recover_habit
from models import UserAchievement, Achievement, Session

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    today = datetime.utcnow().date()
    
    # Fetch Habits
    user_habits = Habit.query.filter_by(user_id=current_user.id).all()
    habit_data = []
    today_habits_js = []
    habit_distribution = {}
    
    for habit in user_habits:
        logs = habit.logs
        check_hour = habit.start_time.hour if habit.start_time else 9
        probability = predict_completion_probability(current_user.id, habit.id, check_hour)
        
        best_hour, best_prob = recommend_best_time(current_user.id, habit.id)
        best_time_display = f"{best_hour % 12 or 12} {'AM' if best_hour < 12 else 'PM'}"
        
        impact = calculate_impact_analysis(logs)
        suggestions = get_suggestions(habit.name, logs)
        
        today_log = HabitLog.query.filter_by(habit_id=habit.id, date=today).first()
        today_completed = (today_log is not None)
        streak = calculate_habit_streak(habit.id, current_user.id)
        
        # Check recovery availability
        recovery_available = can_recover_habit(habit, current_user) if not today_log else False
        
        habit_obj = {
            'habit': habit,
            'probability': probability,
            'best_time': best_time_display,
            'best_prob': best_prob,
            'impact': impact,
            'completed_today': today_completed,
            'suggestions': suggestions,
            'current_streak': streak,
            'recovery_available': recovery_available,
            'today_log': today_log
        }
        habit_data.append(habit_obj)
        
        today_habits_js.append({
            'id': habit.id,
            'name': habit.name,
            'startTime': habit.start_time.strftime('%H:%M') if habit.start_time else None,
            'endTime': habit.end_time.strftime('%H:%M') if habit.end_time else None,
            'completed': today_completed,
            'completion_type': today_log.completion_type if today_log else None,
            'frequency': habit.frequency
        })
        
        total_completions = sum(1 for log in logs if log.status)
        if total_completions > 0:
            habit_distribution[habit.name] = total_completions

    # Heatmap & Stats calculations (Keeping existing logic)
    one_year_ago = today - timedelta(days=365)
    logs = HabitLog.query.join(Habit).filter(
        Habit.user_id == current_user.id, 
        HabitLog.date >= one_year_ago,
        HabitLog.status == True
    ).all()
    
    daily_counts = {}
    for log in logs:
        d_str = log.date.strftime('%Y-%m-%d')
        daily_counts[d_str] = daily_counts.get(d_str, 0) + 1
        
    heatmap_data = []
    for i in range(366):
        d = one_year_ago + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        count = daily_counts.get(d_str, 0)
        level = 0
        if count > 0: level = 1
        if count > 2: level = 2
        if count > 4: level = 3
        if count > 6: level = 4
        heatmap_data.append({'date': d_str, 'count': count, 'level': level})
        
    weekly_labels = []
    weekly_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        weekly_labels.append(d.strftime('%a'))
        weekly_data.append(daily_counts.get(d_str, 0))

    total_contributions = sum(daily_counts.values())
    this_month_count = 0
    monthly_map = {}
    for d_str, count in daily_counts.items():
        if count > 0:
            date_obj = datetime.strptime(d_str, '%Y-%m-%d').date()
            m_key = date_obj.strftime('%Y-%m')
            monthly_map[m_key] = monthly_map.get(m_key, 0) + count
            if date_obj.year == today.year and date_obj.month == today.month:
                this_month_count += count

    monthly_labels = []
    monthly_values = []
    for i in range(11, -1, -1):
        target_year = today.year
        target_month = today.month - i
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        m_label_human = datetime(target_year, target_month, 1).strftime('%b')
        m_key = f"{target_year}-{target_month:02d}"
        monthly_labels.append(m_label_human)
        monthly_values.append(monthly_map.get(m_key, 0))
    
    current_streak = 0
    check_date = today
    while True:
        d_str = check_date.strftime('%Y-%m-%d')
        if daily_counts.get(d_str, 0) > 0:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            if check_date == today:
                 check_date -= timedelta(days=1)
                 continue
            break

    productivity_window = get_productivity_window(current_user.id)
    risky_habits = get_risky_habits(current_user.id)
    user_xp = current_user.xp if current_user.xp else 0
    user_level = (user_xp // 100) + 1
    xp_progress = user_xp % 100

    return render_template('dashboard.html', 
                         user=current_user, 
                         habits=habit_data, 
                         today=today, 
                         heatmap_data=heatmap_data,
                         total_contributions=total_contributions,
                         current_streak=current_streak,
                         weekly_labels=weekly_labels,
                         weekly_data=weekly_data,
                         habit_distribution=habit_distribution,
                         this_month_count=this_month_count,
                         monthly_labels=monthly_labels,
                         monthly_values=monthly_values,
                         user_level=user_level,
                         xp_progress=xp_progress,
                         today_habits_js=today_habits_js,
                         productivity_window=productivity_window,
                         risky_habits=risky_habits)

@dashboard_bp.route('/leaderboard')
@login_required
def leaderboard():
    top_users = User.query.order_by(User.xp.desc()).limit(20).all()
    leaderboard_data = []
    for u in top_users:
        lvl = ((u.xp if u.xp else 0) // 100) + 1
        leaderboard_data.append({
            'username': u.username,
            'xp': u.xp if u.xp else 0,
            'level': lvl,
            'is_current': (u.id == current_user.id)
        })
    return render_template('leaderboard.html', users=leaderboard_data)

@dashboard_bp.route('/achievements')
@login_required
def achievements():
    # Fetch all achievements
    all_achievements = Achievement.query.all()
    # Fetch user's earned achievements
    earned = UserAchievement.query.filter_by(user_id=current_user.id).all()
    earned_ids = {ua.achievement_id: ua for ua in earned}
    
    achievements_data = []
    for ach in all_achievements:
        ua = earned_ids.get(ach.id)
        achievements_data.append({
            'achievement': ach,
            'unlocked': ua is not None,
            'earned_date': ua.earned_at if ua else None
        })
        
    return render_template('achievements.html', user=current_user, achievements=achievements_data)

@dashboard_bp.route('/session/<int:session_id>')
@login_required
def session_mode(session_id):
    session_obj = Session.query.get_or_404(session_id)
    if session_obj.user_id != current_user.id:
        return redirect(url_for('dashboard.dashboard'))
    
    if session_obj.status != 'active':
        # If already completed or cancelled, don't allow resuming
        return redirect(url_for('dashboard.dashboard'))
        
    return render_template('session_mode.html', session=session_obj)
