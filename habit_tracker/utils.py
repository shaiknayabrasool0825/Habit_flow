from datetime import datetime, timedelta
from models import HabitLog

def can_recover_habit(habit, user):
    """
    Checks if a habit can be recovered for yesterday.
    Rules:
    1. Yesterday was missed (no log).
    2. User hasn't used recovery in last 7 days.
    """
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    
    # Check if already logged yesterday
    if HabitLog.query.filter_by(habit_id=habit.id, date=yesterday).first():
        return False
        
    # Check cooldown
    if user.last_recovery_date:
        days_since_recovery = (today - user.last_recovery_date).days
        if days_since_recovery < 7:
            return False
            
    return True

def update_habit_schedule(habit, new_start_time):
    """Updates habit start time and maintains duration if end_time exists."""
    if habit.start_time and habit.end_time:
        # Calculate duration
        start_dt = datetime.combine(datetime.today(), habit.start_time)
        end_dt = datetime.combine(datetime.today(), habit.end_time)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        duration = end_dt - start_dt
        
        # New times
        new_start_dt = datetime.combine(datetime.today(), new_start_time)
        new_end_dt = new_start_dt + duration
        
        habit.start_time = new_start_dt.time()
        habit.end_time = new_end_dt.time()
    else:
        habit.start_time = new_start_time
