from dotenv import load_dotenv

load_dotenv()

from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    email = 'nayabrasoolshaik4842@gmail.com'
    password = 'Nayab@0786'
    
    u = User.query.filter_by(email=email).first()
    if not u:
        u = User(username='AdminNayab', email=email)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        print(f"Admin account created successfully with email: {email}")
    else:
        u.set_password(password)
        db.session.commit()
        print(f"Admin account password successfully updated to {password}")
