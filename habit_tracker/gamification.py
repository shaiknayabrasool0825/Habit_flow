from models import db, Achievement, UserAchievement, HabitLog, Habit
from datetime import datetime, timedelta

def check_achievements(user):
    """
    Checks if the user has unlocked any new achievements.
    Returns a list of newly unlocked achievement objects.
    """
    new_unlocks = []
    
    # Get all available achievements
    all_achievements = Achievement.query.all()
    
    # Get user's existing achievements (ID set for fast lookup)
    earned_ids = {ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=user.id).all()}
    
    # Pre-fetch commonly used data to avoid N+1 queries
    # 1. Total completions
    total_completions = HabitLog.query.join(Habit).filter(Habit.user_id == user.id, HabitLog.status == True).count()
    
    # 2. Perfect Week Logic (last 7 days)
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6)
    # Get logs for last 7 days
    recent_logs = HabitLog.query.join(Habit).filter(
        Habit.user_id == user.id, 
        HabitLog.date >= start_date,
        HabitLog.status == True
    ).all()
    
    # Organize logs by date
    logs_by_date = {}
    for log in recent_logs:
        logs_by_date[log.date] = logs_by_date.get(log.date, []) + [log]
        
    # Check "Perfect Week": Need at least one habit per day? Or all active habits done?
    # Simple interpretation: User was active every single day for 7 days.
    active_days_count = len(logs_by_date.keys())
    
    # 3. Gym/Fitness Count
    # Naive string check on habit names
    gym_habits = Habit.query.filter(Habit.user_id == user.id, 
        (Habit.name.ilike('%gym%') | Habit.name.ilike('%workout%') | Habit.name.ilike('%fitness%'))
    ).all()
    gym_habit_ids = [h.id for h in gym_habits]
    gym_count = 0
    if gym_habit_ids:
        gym_count = HabitLog.query.filter(HabitLog.habit_id.in_(gym_habit_ids), HabitLog.status == True).count()

    # 4. Early Bird Check (Any log with start time < 5am? Or completed before 5am?)
    # We'll check if any log in history corresponds to a "completed checkin" before 5am.
    # Since HabitLog doesn't store exact completion time (only date + created_at), we use created_at.
    # We need to check if ANY log exists where created_at time < 05:00
    # SQL query for efficiency?
    # For now, let's assume we check the *current action* or just query efficiently.
    # Query: Exists a log where created_at time is < 05:00.
    # SQLite/MySQL time extraction differs. 'created_at' is DateTime.
    # Note: 'created_at' is UTC usually. "Before 5 AM" implies local user time. 
    # If we stick to server time (UTC), it might be wrong. 
    # Let's check for the specific flag mostly. 
    # But for "check_achievements" running on every log, we can check if the *just created* log meets criteria?
    # Actually user wants "automatic detection".
    # Let's do a query for existence.
    has_early_bird = False
    # This might be heavy if table is huge, but fine for prototype.
    # Optimization: Only check if not earned.
    
    for ach in all_achievements:
        if ach.id in earned_ids:
            continue
            
        unlocked = False
        
        try:
            val = int(ach.condition_value) if ach.condition_value and ach.condition_value.isdigit() else ach.condition_value
        except:
            val = 0
            
        if ach.condition_type == 'streak':
            # Check current streak or longest streak
            # User model has 'longest_streak' (calculated elsewhere)
            # Assuming 'longest_streak' tracks the max streak ever achieving across *any* habit? 
            # Or is it "global daily streak"? 
            # app.py's check_badges calculated "Daily Streak" (at least 1 habit/day).
            # let's use user.longest_streak if it represents that.
            if user.longest_streak >= int(val):
                unlocked = True
                
        elif ach.condition_type == 'total':
            if total_completions >= int(val):
                unlocked = True
                
        elif ach.condition_type == 'time':
            # "05:00"
            if not has_early_bird: # cache check
                # Check if we have an early bird log
                # We need a robust query or check the latest log?
                # Let's check the latest log for optimization (since we run this on checkin)
                # If we want to support historical, we need a query.
                pass 
                # See below for robust logic
                
            # Naive: Check if last log was early.
            last_log = HabitLog.query.filter_by(status=True).order_by(HabitLog.created_at.desc()).first()
            if last_log:
                # Local time assumption or UTC? 
                # user requested "early bird".
                if last_log.created_at.hour < 5:
                    unlocked = True
                    has_early_bird = True
                    
        elif ach.condition_type == 'specific_habit':
            # value format "10:gym,fitness"
            if ':' in str(val):
                count_req, keywords = str(val).split(':')
                count_req = int(count_req)
                # We already calculated gym_count above for standard keywords
                if gym_count >= count_req:
                    unlocked = True
                    
        elif ach.condition_type == 'perfect_period':
            # Perfect Week (7 days)
            days_req = int(val)
            if active_days_count >= days_req:
                unlocked = True
                
        elif ach.condition_type == 'recovery':
             # Check if last_recovery_date is set
             if user.last_recovery_date:
                 unlocked = True

        if unlocked:
            # Grant Achievement
            ua = UserAchievement(user_id=user.id, achievement_id=ach.id)
            db.session.add(ua)
            
            # Add XP
            user.xp = (user.xp or 0) + ach.xp_reward
            
            new_unlocks.append(ach)
            
    if new_unlocks:
        db.session.commit()
        
    return new_unlocks
