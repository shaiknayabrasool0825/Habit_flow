from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    xp = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_recovery_date = db.Column(db.Date, nullable=True) # New: Track last streak recovery
    timezone = db.Column(db.String(50), default='UTC')
    theme = db.Column(db.String(20), default='system')
    habits = db.relationship('Habit', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Habit(db.Model):
    __tablename__ = 'habits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    frequency = db.Column(db.String(50), default='Daily') # Daily, Weekly
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    color = db.Column(db.String(20), default="blue")
    icon = db.Column(db.String(10), default="⭐")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade="all, delete-orphan")

class HabitLog(db.Model):
    __tablename__ = 'habit_logs'
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    status = db.Column(db.Boolean, default=True) # True = Counts towards streak (Completed, Late, Recovered, Partial)
    completion_type = db.Column(db.String(20), default='completed') # completed, late, recovered, partial
    xp_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('habit_id', 'date', name='_habit_date_uc'),)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50)) # e.g. '🔥', '🏆', 
    xp_reward = db.Column(db.Integer, default=50)
    condition_type = db.Column(db.String(50), nullable=False) # streak, total, time, specific_habit, perfect_period
    condition_value = db.Column(db.String(50), nullable=True) # "3", "7", "05:00"

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    achievement = db.relationship('Achievement')
    user = db.relationship('User', backref=db.backref('achievements', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='_user_achievement_uc'),)

class Suggestion(db.Model):
    __tablename__ = 'suggestions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'time_change', 'frequency_reduction', 'general'
    message = db.Column(db.String(255), nullable=False)
    suggested_value = db.Column(db.String(50)) # e.g., '18:00:00' or 'Weekly'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_dismissed = db.Column(db.Boolean, default=False)

    habit = db.relationship('Habit', backref=db.backref('suggestions', lazy=True, cascade="all, delete-orphan"))
    user = db.relationship('User', backref=db.backref('suggestions', lazy=True, cascade="all, delete-orphan"))

class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending') # 'pending', 'accepted'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id])
    friend = db.relationship('User', foreign_keys=[friend_id])

class WeeklyReport(db.Model):
    __tablename__ = 'weekly_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)
    week_end_date = db.Column(db.Date, nullable=False)
    completion_rate = db.Column(db.Float, default=0.0)
    best_day = db.Column(db.String(20)) # e.g. "Monday"
    worst_day = db.Column(db.String(20))
    strongest_habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=True)
    weakest_habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=True)
    suggestion_text = db.Column(db.Text, nullable=True)
    best_day_rate = db.Column(db.Float, default=0.0)
    worst_day_rate = db.Column(db.Float, default=0.0)
    total_checkins = db.Column(db.Integer, default=0)
    prev_week_diff = db.Column(db.Float, nullable=True)
    xp_bonus_awarded = db.Column(db.Boolean, default=False)
    next_week_plan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('weekly_reports', lazy=True))
    # Using foreign_keys to distinguish between two relationships to the same table
    strongest_habit = db.relationship('Habit', foreign_keys=[strongest_habit_id])
    weakest_habit = db.relationship('Habit', foreign_keys=[weakest_habit_id])


class Session(db.Model):
    """
    Session Mode: active focus session with a timer.
    """
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    planned_duration = db.Column(db.Integer, nullable=False) # minutes
    status = db.Column(db.String(20), default='active', nullable=False) # active, completed, cancelled
    end_time = db.Column(db.DateTime, nullable=True)
    reflection = db.Column(db.String(50), nullable=True) # Energizing, Neutral, Difficult, Avoided
    
    # Relationships
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    habit = db.relationship('Habit', backref=db.backref('sessions', lazy=True))


def calculate_habit_streak(habit_id, user_id):
    """
    Calculates the current streak for a specific habit.
    Considers types: completed, late, recovered, partial.
    """
    # Get all successful logs sorted by date desc
    logs = HabitLog.query.filter_by(habit_id=habit_id, status=True).order_by(HabitLog.date.desc()).all()
    
    if not logs:
        return 0
        
    today = datetime.utcnow().date()
    current_streak = 0
    
    # Check if the most recent log is today or yesterday
    last_log_date = logs[0].date
    
    # If last log was before yesterday, streak is broken (unless covered by recovery, but recovery creates a log)
    if last_log_date < today - timedelta(days=1):
        return 0
        
    # Iterate to count consecutive days
    # We need to act as if we are checking day by day backwards
    check_date = last_log_date
    
    # Map dates to logs for easy lookup
    log_map = {log.date: log for log in logs}
    
    while True:
        if check_date in log_map:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break
            
    return current_streak
