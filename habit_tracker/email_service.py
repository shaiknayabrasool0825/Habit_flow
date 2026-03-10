from flask_mail import Message
from flask import current_app

def _get_mail():
    return current_app.extensions['mail']

def send_habit_reminder(user_email, habit_name, start_time_str, streak):
    # Subject: Habit Reminder — Reading 📚
    # Body: Your habit "Reading" starts at 9:00 PM. Don't break your 4-day streak 🔥
    try:
        mail = _get_mail()
        msg = Message(f"Habit Reminder — {habit_name} 📚", recipients=[user_email])
        msg.body = f"Your habit \"{habit_name}\" starts at {start_time_str}.\nDon't break your {streak}-day streak 🔥"
        mail.send(msg)
        print(f"[Email] Reminder sent to {user_email} for '{habit_name}'")
    except Exception as e:
        print(f"[Email Error] {e}")

def send_daily_summary(user_email, completed_count, total_count):
    # Subject: Daily Summary 🌙
    # Body: You completed 3/5 habits today. Keep it up!
    try:
        mail = _get_mail()
        msg = Message("Daily Summary 🌙", recipients=[user_email])
        msg.body = f"You completed {completed_count}/{total_count} habits today.\n\nKeep consistent to reach your goals!"
        mail.send(msg)
        print(f"[Email] Daily summary sent to {user_email}")
    except Exception as e:
        print(f"[Email Error] {e}")

def send_weekly_report(user_email, completion_rate, best_day, worst_day):
    # Subject: Your Weekly Report 📊
    # Body: Completion Rate: 75%\nBest Day: Monday\nWorst Day: Thursday
    try:
        mail = _get_mail()
        msg = Message("Your Weekly Report 📊", recipients=[user_email])
        msg.body = (f"Here is your weekly progress:\n\n"
                    f"Completion Rate: {completion_rate}%\n"
                    f"Best Day: {best_day}\n"
                    f"Worst Day: {worst_day}\n\n"
                    f"Check your dashboard for full insights and coach suggestions!")
        mail.send(msg)
        print(f"[Email] Weekly report sent to {user_email}")
    except Exception as e:
        print(f"[Email Error] {e}")

def send_welcome_email(user_email, username):
    # Subject: Welcome to Habit Tracker! 🚀
    try:
        mail = _get_mail()
        msg = Message("Welcome to Habit Tracker! 🚀", recipients=[user_email])
        msg.body = (f"Hi {username}!\n\n"
                    f"Welcome to your new Habit Tracker. We're excited to help you build better habits!\n\n"
                    f"Get started by adding your first habit on your dashboard.\n\n"
                    f"If you have any questions, feel free to reply to this email.\n\n"
                    f"Happy tracking!\n"
                    f"- The Habit Tracker Team")
        mail.send(msg)
        print(f"[Email] Welcome email sent to {user_email}")
    except Exception as e:
        print(f"[Email Error] {e}")

def send_reset_email(to_email, reset_url):
    try:
        mail = _get_mail()
        msg = Message("HabitFlow - Password Reset Request", recipients=[to_email])
        msg.body = f'''To securely reset your HabitFlow password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email and nothing will be changed.
'''
        msg.html = f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
            <h2 style="color: #4f46e5;">Password Reset Request</h2>
            <p>A password reset was requested for your HabitFlow account.</p>
            <p>To securely reset your password, click the button below:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Reset Password</a>
            </div>
            <p style="font-size: 0.9em; color: #64748b;">If you did not request this email, you can safely ignore it.</p>
        </div>
        '''
        mail.send(msg)
        print(f"[Email] Password reset link successfully dispatched to {to_email}")
        return True
    except Exception as e:
        print(f"[Email Error] Failed to send password reset: {e}")
        return False
