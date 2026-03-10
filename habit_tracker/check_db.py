from app import create_app
from models import db, Habit
import os

app = create_app('dev')
with app.app_context():
    try:
        # Check if color exists in habits
        h = Habit.query.first()
        if h:
            print(f"Color: {h.color}")
        else:
            print("No habits found")
    except Exception as e:
        print(f"DB Error: {e}")
