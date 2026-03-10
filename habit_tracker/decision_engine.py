from datetime import datetime, time
from models import Habit, HabitLog, calculate_habit_streak, db
from ml_logic import predict_completion_probability
from smart_coach import get_action_explanation

def get_next_action(user_id):
    """
    Finds the highest priority habit currently in its active time window.
    """
    habits = Habit.query.filter_by(user_id=user_id).all()
    today = datetime.utcnow().date()
    now_time = datetime.utcnow().time()
    
    active_habits = []
    
    for habit in habits:
        # Check if completed today
        if HabitLog.query.filter_by(habit_id=habit.id, date=today).first():
            continue
            
        # Check time window
        if not habit.start_time or not habit.end_time:
            # If no time, assume active? Or ignore for "immediate" action?
            # User wants "immediate" action based on time windows.
            continue
            
        # Check if now is within [start_time, end_time]
        is_active = False
        if habit.start_time <= habit.end_time:
            is_active = habit.start_time <= now_time <= habit.end_time
        else: # Overnight window e.g. 10 PM to 2 AM
            is_active = now_time >= habit.start_time or now_time <= habit.end_time
            
        if is_active:
            # Get probability & streak
            prob = predict_completion_probability(user_id, habit.id, now_time.hour)
            streak = calculate_habit_streak(habit.id, user_id)
            
            # Compute score: prob + streak bonus
            priority_score = prob + (streak * 0.05)
            
            active_habits.append({
                "habit": habit,
                "score": priority_score,
                "probability": prob,
                "streak": streak
            })
            
    if not active_habits:
        return {
            "habit_id": None,
            "next_action": "Rest & Refuel",
            "success_probability": None,
            "window": "Off-peak",
            "reason": "No active habit window. Recommend planning or hydration.",
            "cta_label": "Go To Dashboard"
        }
        
    # Pick best
    best = max(active_habits, key=lambda x: x["score"])
    h = best["habit"]
    
    window_str = f"{h.start_time.strftime('%H:%M')} - {h.end_time.strftime('%H:%M')}"
    reason = get_action_explanation(h, best["probability"], best["streak"])
    
    return {
        "habit_id": h.id,
        "next_action": h.name,
        "success_probability": best["probability"],
        "window": window_str,
        "reason": reason,
        "cta_label": "Start Session"
    }
