from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            username = request.form.get('username')
            # Assuming we only allow updating timezone and theme
            timezone = request.form.get('timezone', 'UTC')
            theme = request.form.get('theme', 'system')
            
            user = User.query.get(current_user.id)
            if username:
                user.username = username
            user.timezone = timezone
            user.theme = theme
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.settings'))
            
        elif action == 'delete_account':
            user = User.query.get(current_user.id)
            from models import Habit, HabitLog, Suggestion, UserAchievement, WeeklyReport, Session, Friendship
            from flask_login import logout_user
            
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
            db.session.commit()
            
            logout_user()
            flash('Your account and all associated data have been permanently deleted.', 'success')
            return redirect(url_for('dashboard.home'))

    return render_template('profile.html', user=current_user)
