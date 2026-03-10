from datetime import datetime, timedelta, time
from models import db, Habit, HabitLog, Suggestion

def analyze_user_habits(user_id):
    """
    Analyzes user's habits and generates suggestions based on performance.
    """
    habits = Habit.query.filter_by(user_id=user_id).all()
    today = datetime.utcnow().date()
    
    # Clean up old dismissed suggestions? Or keep them for history?
    # For now, let's just generate new ones if they don't exist active.
    
    # ML-Based Smart Suggestions 
    from ml_logic import predict_completion_probability, recommend_best_time, predict_failure_probability

    for habit in habits:
        # Check active suggestions for this habit
        active_suggestion = Suggestion.query.filter_by(
            habit_id=habit.id, 
            is_dismissed=False
        ).first()
        
        if active_suggestion:
            continue # Skip if already has a suggestion

        days_active = (today - habit.created_at.date()).days
        if days_active < 3:
            continue # Too new for ML

        # Predict current probability
        # If habit has a start_time, use that hour. Else use default (e.g. 9 AM or current time context?)
        # For a "general" suggestion, we check the scheduled time.
        check_hour = habit.start_time.hour if habit.start_time else 9
        
        current_prob = predict_completion_probability(user_id, habit.id, check_hour)
        
        # Threshold: If < 40% chance of success
        if current_prob < 40:
            # Find best time
            best_hour, best_prob = recommend_best_time(user_id, habit.id)
            
            # If significantly better (> 60% or +20% boost)
            if best_prob > (current_prob + 20):
                # Format time
                best_time_str = f"{best_hour:02d}:00:00" # HH:MM:SS
                best_time_display = f"{best_hour % 12 or 12} {'AM' if best_hour < 12 else 'PM'}"
                
                create_suggestion(user_id, habit.id, 'time_change',
                                  f"You are likely to miss '{habit.name}' at its current time ({current_prob}% chance). Try {best_time_display} instead ({best_prob}% chance).",
                                  best_time_str)
            else:
                # If no better time, suggest reducing frequency?
                if habit.frequency == 'Daily':
                    create_suggestion(user_id, habit.id, 'frequency_reduction',
                                      f"'{habit.name}' seems tough daily ({current_prob}% success chance). Switch to Weekly?",
                                      'Weekly')
                                      
        # Check Failure Risk Probability for critical warnings (next 24-48 hours)
        today_log = HabitLog.query.filter_by(habit_id=habit.id, date=today).first()
        if not (today_log and today_log.status):
            failure_risk = predict_failure_probability(user_id, habit.id)
            if failure_risk > 0.7:
                # Generate a critical warning if failure risk is very high
                warning_msg = f"High Risk Alert ({(failure_risk*100):.0f}%): You are highly likely to miss '{habit.name}' today. Try to prepare your environment or reduce the scope to just 2 minutes to save your streak!"
                create_suggestion(user_id, habit.id, 'critical_warning', warning_msg, 'Prepare Environment')

def create_suggestion(user_id, habit_id, type, message, suggested_value):
    suggestion = Suggestion(
        user_id=user_id,
        habit_id=habit_id,
        type=type,
        message=message,
        suggested_value=suggested_value
    )
    db.session.add(suggestion)
    db.session.commit()


from models import WeeklyReport, User

def get_week_feedback(completion_rate):
    if completion_rate >= 80:
        return "Excellent discipline this week 🔥"
    elif completion_rate >= 60:
        return "Good progress — you’re building consistency."
    elif completion_rate >= 40:
        return "You’re getting started. Let’s improve next week."
    else:
        return "Rough week — let’s reset and simplify your habits."

def generate_coach_suggestion(user_id, habits, logs, completion_rate, weakest_habit, worst_day, worst_day_rate):
    # Rule 1: Morning vs Evening
    morning_success = 0
    evening_success = 0
    morning_total = 0
    evening_total = 0
    
    # We need time info. Logs don't have time, but Habits have start_time.
    # Associate logs with habits and check habit.start_time
    for h in habits:
        if not h.start_time: continue
        
        h_logs = [l for l in logs if l.habit_id == h.id and l.status]
        count = len(h_logs)
        
        if h.start_time.hour < 12:
            morning_total += 1 # Count habits, not logs? Or logs? Logs indicate performance.
            morning_success += count
        elif h.start_time.hour >= 20: # 8 PM
            evening_total += 1
            evening_success += count
            
    # Normalize? Or just raw comparison?
    # "IF most completions occur before noon" -> simple sum comparison
    if morning_success > (len(logs) * 0.6): # 60% of all completions
        return "You perform better in the morning. Move difficult habits earlier."
        
    # "IF many misses after 8PM"
    # Hard to track misses without expected count per time slot.
    # Approximate: If evening habits have low rate?
    if evening_total > 0:
        # Calculate rate for evening habits
        # This is complex without pre-calc.
        pass

    # Rule: Low success rate habit
    if weakest_habit:
        # Recalculate weakest rate or pass it in?
        # We have weakest_habit object.
        pass # We'll handle this in main logic if rate < 40
        
    if weakest_habit and completion_rate < 40: # Weak heuristic
         return f"'{weakest_habit.name}' has low success. Reduce duration or change time."
         
    # Rule: Overloaded day
    # Check if any day has > 4 habits scheduled
    # We need day distribution
    pass 
    
    return "Keep accurate records to get better insights next week."

def generate_weekly_report(user_id):
    """
    Generates a weekly report for the user based on the last 7 days.
    """
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6) # 7 days inclusive: today + 6 previous days

    # Fetch logs
    logs = HabitLog.query.join(Habit).filter(
        Habit.user_id == user_id,
        HabitLog.date >= start_date,
        HabitLog.date <= today,
        HabitLog.status == True
    ).all()

    habits = Habit.query.filter_by(user_id=user_id).all()
    if not habits:
        return None # No habits, no report

    # --- 1. Completion Rate ---
    total_completed = len(logs)
    total_checkins = total_completed
    total_expected = 0
    
    # Calculate expected
    habit_expectations = {}
    for h in habits:
        days_active = (today - h.created_at.date()).days + 1
        days_in_period = min(7, days_active)
        days_in_period = max(0, days_in_period)
        
        expected = 0
        if h.frequency == 'Daily':
            expected = days_in_period
        else: # Weekly
            expected = 1 if days_in_period > 0 else 0
            
        total_expected += expected
        habit_expectations[h.id] = expected

    completion_rate = (total_completed / total_expected * 100) if total_expected > 0 else 0.0
    completion_rate = round(completion_rate, 1)

    # --- 2. Best & Worst Day ---
    days_stats = {i: {'completed': 0, 'expected': 0} for i in range(7)}
    
    # Fill Expected
    for i in range(7):
        current_day_date = start_date + timedelta(days=i)
        weekday = current_day_date.weekday()
        for h in habits:
            if h.created_at.date() <= current_day_date:
                if h.frequency == 'Daily':
                    days_stats[weekday]['expected'] += 1
                elif h.frequency == 'Weekly':
                     pass 

    # Fill Completed
    for log in logs:
         weekday = log.date.weekday()
         days_stats[weekday]['completed'] += 1
         
    # Calculate rates
    day_rates = []
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i in range(7):
        exp = days_stats[i]['expected']
        comp = days_stats[i]['completed']
        rate = (comp / exp * 100) if exp > 0 else 0.0
        day_rates.append({'day': weekdays[i], 'rate': rate, 'expected': exp})
        
    # Best Day & Worst Day
    active_days = [d for d in day_rates if d['expected'] > 0]
    if active_days:
        best_day_obj = max(active_days, key=lambda x: x['rate'])
        worst_day_obj = min(active_days, key=lambda x: x['rate'])
        
        best_day = best_day_obj['day']
        best_day_rate = round(best_day_obj['rate'], 1)
        worst_day = worst_day_obj['day']
        worst_day_rate = round(worst_day_obj['rate'], 1)
    else:
        best_day = "N/A"
        best_day_rate = 0.0
        worst_day = "N/A"
        worst_day_rate = 0.0

    # --- 3. Strongest & Weakest Habit ---
    habit_stats = {}
    for h in habits:
        h_logs = [l for l in logs if l.habit_id == h.id]
        comp = len(h_logs)
        exp = habit_expectations.get(h.id, 0)
        rate = (comp / exp * 100) if exp > 0 else 0.0
        habit_stats[h.id] = {'habit': h, 'rate': rate, 'completed': comp, 'expected': exp}
        
    if habit_stats:
        strongest_h_id = max(habit_stats, key=lambda k: habit_stats[k]['rate'])
        weakest_h_id = min(habit_stats, key=lambda k: habit_stats[k]['rate'])
        
        strongest_habit = habit_stats[strongest_h_id]['habit']
        weakest_habit = habit_stats[weakest_h_id]['habit']
        weakest_rate = habit_stats[weakest_h_id]['rate']
    else:
        strongest_habit = None
        weakest_habit = None
        weakest_rate = 0

    # --- 4. Suggestions & Plan ---
    
    # Generate Suggestion
    suggestion_text = generate_coach_suggestion(
        user_id, habits, logs, completion_rate, weakest_habit, worst_day, worst_day_rate
    )
    # Refined logic for suggestion if helper returns default
    if suggestion_text == "Keep accurate records to get better insights next week.":
        # Fallbacks
        if weakest_habit and weakest_rate < 40:
             suggestion_text = f"'{weakest_habit.name}' has low success ({int(weakest_rate)}%). Reduce duration or change time."
        elif worst_day != "N/A" and worst_day_rate < 40:
             suggestion_text = f"Try scheduling easier habits on {worst_day}."
        elif completion_rate < 50:
             suggestion_text = "Rough week — let’s reset and simplify your habits."

    # Generate Plan
    plan_lines = []
    if strongest_habit:
        plan_lines.append(f"✅ Keep '{strongest_habit.name}' at same time.")
    if weakest_habit and weakest_rate < 50:
        plan_lines.append(f"⚠️ Consider moving '{weakest_habit.name}' to a better slot.")
    if worst_day != "N/A" and worst_day_rate < 50:
        plan_lines.append(f"📅 Lighten load on {worst_day}.")
    
    target_rate = min(100, completion_rate + 5)
    plan_lines.append(f"🚀 Target {int(target_rate)}% completion next week.")
    
    next_week_plan = "\n".join(plan_lines)

    # --- 5. Comparison & XP ---
    
    # Previous Week
    prev_report = WeeklyReport.query.filter_by(user_id=user_id)\
        .order_by(WeeklyReport.created_at.desc()).first()
        
    prev_week_diff = None
    if prev_report:
        prev_week_diff = round(completion_rate - prev_report.completion_rate, 1)

    # XP Bonus
    xp_bonus = 0
    if completion_rate >= 80: xp_bonus = 50
    elif completion_rate >= 60: xp_bonus = 35
    elif completion_rate >= 40: xp_bonus = 15
    else: xp_bonus = 5
    
    user = User.query.get(user_id)
    user.xp += xp_bonus
    xp_bonus_awarded = True

    # Save Report
    report = WeeklyReport(
        user_id=user_id,
        week_start_date=start_date,
        week_end_date=today,
        completion_rate=completion_rate,
        best_day=best_day,
        worst_day=worst_day,
        best_day_rate=best_day_rate,
        worst_day_rate=worst_day_rate,
        strongest_habit_id=strongest_habit.id if strongest_habit else None,
        weakest_habit_id=weakest_habit.id if weakest_habit else None,
        suggestion_text=suggestion_text,
        total_checkins=total_checkins,
        prev_week_diff=prev_week_diff,
        xp_bonus_awarded=xp_bonus_awarded,
        next_week_plan=next_week_plan
    )
    db.session.add(report)
    db.session.commit()
    
    return report

def get_action_explanation(habit, probability, streak):
    """
    Generates a short encouraging explanation for why a habit is recommended.
    """
    if streak > 5:
        return f"You're on a massive {streak}-day streak! Don't let the momentum stop now. Your success chance is {probability}%."
    if probability > 80:
        return f"Conditions are perfect for {habit.name}. You have a very high {probability}% chance of success right now."
    if probability < 40:
        return f"This habit might be challenging right now ({probability}% chance). Completing it will give you a major discipline boost!"
    
    return f"It's the scheduled window for {habit.name}. Focus for just a few minutes to keep your progress going."
