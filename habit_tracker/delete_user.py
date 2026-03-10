import sys
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from models import db, User, Habit, HabitLog, Suggestion, UserAchievement, WeeklyReport, Session, Friendship

def delete_user_by_email(email):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"User with email {email} not found!")
            return False
            
        print(f"Found User: {user.username} (ID: {user.id})")
        print("Commencing deletion of all related data...")
        
        # 1. Delete Friendships manually
        Friendship.query.filter((Friendship.user_id == user.id) | (Friendship.friend_id == user.id)).delete()
        
        # 2. Delete Sessions and Weekly Reports
        Session.query.filter_by(user_id=user.id).delete()
        WeeklyReport.query.filter_by(user_id=user.id).delete()
        
        # 3. Delete Suggestions
        Suggestion.query.filter_by(user_id=user.id).delete()
        
        # 4. Delete User Achievements
        UserAchievement.query.filter_by(user_id=user.id).delete()
        
        # 5. Delete Habits and cascade onto their Habit Logs
        habits = Habit.query.filter_by(user_id=user.id).all()
        for habit in habits:
            HabitLog.query.filter_by(habit_id=habit.id).delete()
            db.session.delete(habit)
            
        # 6. Finally, delete the User
        db.session.delete(user)
        
        # Commit all transactions at once safely
        db.session.commit()
        print(f"Successfully deleted {user.username} and all their associated data from the database.")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_user.py <user_email>")
        sys.exit(1)
        
    target_email = sys.argv[1]
    delete_user_by_email(target_email)
