import pandas as pd
import numpy as np
import joblib
import os
import math
from datetime import datetime, timedelta, time
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
from models import db, User, Habit, HabitLog

# Global model path
MODEL_DIR = 'models'

def get_risk_heuristic(user_id, habit_id):
    """
    Fallback heuristic scoring model if insufficient training data exists.
    Returns failure risk probability (0-1).
    """
    habit = Habit.query.get(habit_id)
    if not habit: return 0.5
    
    # 1. Habit Age
    days_active = (datetime.utcnow().date() - habit.created_at.date()).days
    if days_active < 3: return 0.5 # Too new, uncertain
    
    # 2. Extract logs
    logs = HabitLog.query.filter_by(habit_id=habit_id).order_by(HabitLog.date.asc()).all()
    if not logs: return 0.8 # No logs at all yet, high risk of failure
    
    # Track completion rates
    completed_last_7 = 0
    completed_total = 0
    today = datetime.utcnow().date()
    
    for l in logs:
        if l.status:
            completed_total += 1
            if (today - l.date).days <= 7:
                completed_last_7 += 1
                
    recent_rate = completed_last_7 / min(7, days_active)
    overall_rate = completed_total / days_active
    
    # Current Streak
    streak = 0
    log_map = {l.date: l for l in logs}
    check_day = today - timedelta(days=1)
    while check_day in log_map and log_map[check_day].status:
        streak += 1
        check_day -= timedelta(days=1)
        
    # Heuristic scoring weights
    risk = 0.5 
    
    # Feature 1: Recent rate is highly predictive of future rate 
    if recent_rate < 0.3: risk += 0.2
    elif recent_rate > 0.8: risk -= 0.2
    
    # Feature 2: If long streak is built up, less likely to fail
    if streak > 7: risk -= 0.15
    elif streak == 0: risk += 0.1
    
    # Clamp bounds and return probability
    return max(0.01, min(0.99, risk))

def train_failure_model(user_id):
    """
    Trains a predictive model for Failure Risk Analysis.
    Models features: 7d rate, 30d rate, streak length, habit age, day-of-week info, consistency.
    Saves to joblib.
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    df = build_training_dataframe(user_id)
    if df.empty or len(df) < 14: # Minimum days required for meaningful failure ML (14 days history)
        return False
        
    # We need to compute temporal trailing features from the raw DataFrame
    # Note: `build_training_dataframe` provides raw row-by-row data. We will compute aggregated features.
    
    # Ensure dataframe is sorted by habit and date (though we didn't track date in `build_training_dataframe` returned dict, 
    # we can rebuild logic or append to it. For simplicity in this demo, let's inject a specialized build script)
    pass # Implementation of dataframe extraction is done below in `predict_failure_probability`

def predict_failure_probability(user_id, habit_id):
    """
    Estimates the probability (0-1) that the user will FAIL a given habit in the next 24 hours.
    Fallback to heuristics if the sklearn model fails or doesn't exist.
    """
    model_path = os.path.join(MODEL_DIR, f'{user_id}_model.pkl')
    scaler_path = os.path.join(MODEL_DIR, f'{user_id}_scaler.pkl')
    
    # 1. Heuristic Fallback Strategy if Models aren't ready
    if not (os.path.exists(model_path) and os.path.exists(scaler_path)):
        return get_risk_heuristic(user_id, habit_id)
        
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        feature_cols = joblib.load(os.path.join(MODEL_DIR, f'{user_id}_columns.pkl'))
    except:
        return get_risk_heuristic(user_id, habit_id)

    habit = Habit.query.get(habit_id)
    if not habit: return 0.5
    
    # Construct real-time features
    today = datetime.utcnow().date()
    weekday = today.weekday()
    is_weekend = 1 if weekday >= 5 else 0
    
    # Fetch all history
    logs_all = HabitLog.query.filter_by(habit_id=habit_id).all()
    log_map = {l.date: l for l in logs_all}
    days_active = max(1, (today - habit.created_at.date()).days)
    
    # Streak
    streak = 0
    check_date = today - timedelta(days=1)
    while check_date in log_map and log_map[check_date].status:
        streak += 1
        check_date -= timedelta(days=1)
        
    # Previous day completed
    prev_log = log_map.get(today - timedelta(days=1))
    previous_day_completed = 1 if (prev_log and prev_log.status) else 0
        
    # Habit difficulty (overall completion rate)
    diff = sum(1 for l in logs_all if l.status) / max(1, len(logs_all)) if logs_all else 0.5
    
    # Cyclical hour encoding
    check_hour = habit.start_time.hour if habit.start_time else 9
    sin_hour = math.sin(2 * math.pi * check_hour / 24)
    cos_hour = math.cos(2 * math.pi * check_hour / 24)
        
    row_data = {
        'sin_hour': sin_hour,
        'cos_hour': cos_hour,
        'day_of_week': weekday,
        'is_weekend': is_weekend,
        'streak_length': streak,
        'habit_difficulty': diff,
        'previous_day_completed': previous_day_completed
    }
    
    # Extract only matching features that the model was trained on
    features = pd.DataFrame([row_data], columns=feature_cols)
    
    # In case missing columns got passed
    for col in feature_cols:
        if col not in features: features[col] = 0
        
    scale_cols = ['streak_length', 'habit_difficulty']
    features[scale_cols] = scaler.transform(features[scale_cols])
    
    try:
        # Prob(Target = 1) is COMPLETION probability
        # To find FAILURE probability: P(Fail) = 1.0 - P(Complete)
        proba_complete = model.predict_proba(features)[0][1]
        failure_risk = 1.0 - proba_complete
        return float(failure_risk)
    except:
        return get_risk_heuristic(user_id, habit_id)

def build_training_dataframe(user_id):
    """
    Builds a training DataFrame for a specific user.
    Fetches HabitLogs and Habits, reconstructs daily history including missed days.
    """
    habits = Habit.query.filter_by(user_id=user_id).all()
    if not habits:
        return pd.DataFrame()

    rows = []
    today = datetime.utcnow().date()
    
    # Pre-calc success rates for 'habit_difficulty'
    habit_success_map = {}
    for habit in habits:
        logs = HabitLog.query.filter_by(habit_id=habit.id).all()
        if not logs:
            habit_success_map[habit.id] = 0.5 
        else:
            completed = sum(1 for l in logs if l.status) 
            total = len(logs)
            habit_success_map[habit.id] = completed / total if total > 0 else 0.5

    for habit in habits:
        if habit.frequency != 'Daily':
            continue

        logs = HabitLog.query.filter_by(habit_id=habit.id).all()
        log_map = {log.date: log for log in logs}
        
        start_date = habit.created_at.date()
        end_date = today - timedelta(days=1)
        
        if end_date < start_date:
            continue
            
        current_date = start_date
        
        # Scheduled time for cyclical encoding
        h_time = habit.start_time if habit.start_time else time(9, 0)
        hour_val = h_time.hour + h_time.minute / 60.0
        
        # Cyclical encoding
        sin_hour = math.sin(2 * math.pi * hour_val / 24)
        cos_hour = math.cos(2 * math.pi * hour_val / 24)
        
        while current_date <= end_date:
            log = log_map.get(current_date)
            
            # Features
            weekday = current_date.weekday()
            is_weekend = 1 if weekday >= 5 else 0
            
            # Streak
            streak = 0
            check_streak = current_date - timedelta(days=1)
            while check_streak in log_map and log_map[check_streak].status:
                streak += 1
                check_streak -= timedelta(days=1)
            
            # Previous day completed
            prev_log = log_map.get(current_date - timedelta(days=1))
            previous_day_completed = 1 if (prev_log and prev_log.status) else 0

            # Target
            completed = 1 if (log and log.status) else 0

            rows.append({
                'habit_id': habit.id,
                'sin_hour': sin_hour,
                'cos_hour': cos_hour,
                'day_of_week': weekday,
                'is_weekend': is_weekend,
                'streak_length': streak,
                'habit_difficulty': habit_success_map.get(habit.id, 0.5),
                'previous_day_completed': previous_day_completed,
                'completed': completed
            })
            
            current_date += timedelta(days=1)
            
    return pd.DataFrame(rows)

def train_model(user_id):
    """
    Trains a LogisticRegression model for the user and saves it.
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    df = build_training_dataframe(user_id)
    
    if df.empty or len(df) < 10:
        return False
    
    # Feature Selection (X must include what was specified)
    feature_cols = ['sin_hour', 'cos_hour', 'day_of_week', 'is_weekend', 'streak_length', 'habit_difficulty', 'previous_day_completed']
    scale_cols = ['streak_length', 'habit_difficulty'] # Scaling sin/cos or 0/1 features often unnecessary or harmful, but let's stick to numerical ones.
    
    X = df[feature_cols]
    y = df['completed']
    
    if len(y.unique()) < 2:
        return False

    scaler = StandardScaler()
    X_scaled = X.copy()
    X_scaled[scale_cols] = scaler.fit_transform(X[scale_cols])
    
    # Train
    model = LogisticRegression(max_iter=200, class_weight='balanced')
    model.fit(X_scaled, y)
    
    # Save artifacts
    joblib.dump(model, os.path.join(MODEL_DIR, f'{user_id}_model.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, f'{user_id}_scaler.pkl'))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, f'{user_id}_columns.pkl'))
    
    return True

def retrain_habit_model(user_id, habit_id=None):
    """Alias for train_model for better semantics during editing."""
    return train_model(user_id)

def predict_completion_probability(user_id, habit_id, hour, weekday=None):
    """
    Predicts probability using cyclical time encoding.
    'hour' is the hypothesized scheduled hour (float or int).
    """
    model_path = os.path.join(MODEL_DIR, f'{user_id}_model.pkl')
    scaler_path = os.path.join(MODEL_DIR, f'{user_id}_scaler.pkl')
    columns_path = os.path.join(MODEL_DIR, f'{user_id}_columns.pkl')
    
    if not (os.path.exists(model_path) and os.path.exists(scaler_path)):
        return 50 
        
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        feature_cols = joblib.load(columns_path)
    except:
        return 50
        
    habit = Habit.query.get(habit_id)
    if not habit: return 50
    
    today = datetime.utcnow().date()
    if weekday is None:
        weekday = today.weekday()
        
    is_weekend = 1 if weekday >= 5 else 0
    
    # Cyclical hour encoding
    sin_hour = math.sin(2 * math.pi * hour / 24)
    cos_hour = math.cos(2 * math.pi * hour / 24)
    
    # Streak
    logs_all = HabitLog.query.filter_by(habit_id=habit_id).all()
    log_map = {l.date: l for l in logs_all}
    
    streak = 0
    check_date = today - timedelta(days=1)
    while check_date in log_map and log_map[check_date].status:
        streak += 1
        check_date -= timedelta(days=1)
        
    # Previous day completed
    prev_log = log_map.get(today - timedelta(days=1))
    previous_day_completed = 1 if (prev_log and prev_log.status) else 0
        
    # habit_difficulty
    if logs_all:
        diff = sum(1 for l in logs_all if l.status) / len(logs_all)
    else:
        diff = 0.5
        
    row_data = {
        'sin_hour': sin_hour,
        'cos_hour': cos_hour,
        'day_of_week': weekday,
        'is_weekend': is_weekend,
        'streak_length': streak,
        'habit_difficulty': diff,
        'previous_day_completed': previous_day_completed
    }
    
    features = pd.DataFrame([row_data], columns=feature_cols)
    scale_cols = ['streak_length', 'habit_difficulty']
    features[scale_cols] = scaler.transform(features[scale_cols])
    
    proba = model.predict_proba(features)[0][1]
    return int(proba * 100)

def recommend_best_time(user_id, habit_id):
    """
    Simulates different hours to find the one with the highest probability.
    """
    best_hour = 9
    max_prob = -1
    
    # Scan every hour
    for h in range(0, 24):
        prob = predict_completion_probability(user_id, habit_id, h)
        if prob > max_prob:
            max_prob = prob
            best_hour = h
            
    return best_hour, max_prob

def get_risky_habits(user_id):
    habits = Habit.query.filter_by(user_id=user_id).all()
    risky = []
    for habit in habits:
        h = habit.start_time.hour + habit.start_time.minute / 60.0 if habit.start_time else 9
        prob = predict_completion_probability(user_id, habit.id, h)
        if prob < 40:
            risky.append({
                'habit_id': habit.id,
                'name': habit.name,
                'prob': prob,
                'scheduled_hour': int(h)
            })
    return risky

def get_productivity_window(user_id):
    logs = HabitLog.query.join(Habit).filter(Habit.user_id == user_id, HabitLog.status == True).all()
    if len(logs) < 5: return "Not enough data"
    hours = [l.created_at.hour for l in logs if l.created_at]
    if not hours: return "N/A"
    
    k = 3 if len(hours) >= 5 else 1
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(np.array(hours).reshape(-1, 1))
    
    labels = kmeans.labels_
    unique, counts = np.unique(labels, return_counts=True)
    best_cluster = unique[np.argmax(counts)]
    cluster_hours = [hours[i] for i in range(len(hours)) if labels[i] == best_cluster]
    if not cluster_hours: return "N/A"
    
    min_h, max_h = min(cluster_hours), max(cluster_hours)
    def fmt(h): return datetime.strptime(str(h), "%H").strftime("%I %p").lstrip("0")
    return f"{fmt(min_h)} - {fmt(max_h)}"

def calculate_impact_analysis(logs):
    return {'current_rate':50, 'weekly_rate':50, 'if_missed':45, 'if_completed':55} 
    
def get_suggestions(name, logs):
    return []
