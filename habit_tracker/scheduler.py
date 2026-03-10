from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import atexit
import os

_app = None

# Job Functions
def check_habits():
    global _app
    if not _app: return

    from models import User, Habit, calculate_habit_streak
    from email_service import send_habit_reminder
    
    with _app.app_context():
        # print(f"[{datetime.now()}] Scheduler: Checking habits...")
        users = User.query.all()
        now = datetime.now()
        current_time = now.time()
        today = now.date()
        
        for user in users:
            habits = Habit.query.filter_by(user_id=user.id).all()
            for habit in habits:
                if habit.start_time:
                    # Trigger 5 minutes before start time
                    # Logic: If (start_time - 5min) matches current time (HH:MM)
                    trigger_dt = datetime.combine(today, habit.start_time) - timedelta(minutes=5)
                    
                    if trigger_dt.time().hour == current_time.hour and trigger_dt.time().minute == current_time.minute:
                        # Calculate streak
                        streak = calculate_habit_streak(habit.id, user.id)
                        
                        send_habit_reminder(
                            user.email, 
                            habit.name, 
                            habit.start_time.strftime('%I:%M %p'), 
                            streak
                        )

def run_daily_summary():
    global _app
    if not _app: return

    from models import User, Habit, HabitLog
    from email_service import send_daily_summary
    
    with _app.app_context():
        print("[Scheduler] Running Daily Summary...")
        users = User.query.all()
        today = datetime.now().date()
        
        for user in users:
            habits = Habit.query.filter_by(user_id=user.id).all()
            if not habits: continue
            
            total_habits = len(habits)
            completed_count = 0
            
            for h in habits:
                log = HabitLog.query.filter_by(habit_id=h.id, date=today, status=True).first()
                if log:
                    completed_count += 1
            
            # Send summary
            send_daily_summary(user.email, completed_count, total_habits)

def run_weekly_report():
    global _app
    if not _app: return

    from models import User
    from smart_coach import generate_weekly_report
    from email_service import send_weekly_report
    
    with _app.app_context():
        print("[Scheduler] Running Weekly Report...")
        users = User.query.all()
        
        for user in users:
            # Generate or fetch latest report
            # Force generation for email
            report = generate_weekly_report(user.id)
            
            if report:
                send_weekly_report(
                    user.email, 
                    report.completion_rate, 
                    report.best_day, 
                    report.worst_day
                )


                
def train_all_models():
    global _app
    if not _app: return

    from models import User
    from ml_logic import train_model
    
    with _app.app_context():
        # print("[Scheduler] Training ML models...")
        users = User.query.all()
        for user in users:
            try:
                train_model(user.id)
            except Exception as e:
                print(f"Error training model for user {user.id}: {e}")

# Scheduler Setup
def start_scheduler(app):
    global _app
    _app = app
    
    # Only start if not in debug reload mode or is main process
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        
        # 1. Check Habits (Every 1 minute)
        scheduler.add_job(check_habits, 'interval', minutes=1)
        
        # 2. Daily Summary (Every day at 9 PM)
        # Note: APScheduler 'cron' trigger is good for specific time
        scheduler.add_job(run_daily_summary, 'cron', hour=21, minute=0)
        
        # 3. Weekly Report (Sunday at 7 PM)
        # day_of_week='sun', hour=19
        scheduler.add_job(run_weekly_report, 'cron', day_of_week='sun', hour=19, minute=0)

        # 4. ML Model Training (Daily at 2 AM)
        scheduler.add_job(train_all_models, 'cron', hour=2, minute=0)
        
        scheduler.start()
        print("Scheduler started!")
        
        atexit.register(lambda: scheduler.shutdown())
