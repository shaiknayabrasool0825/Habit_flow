from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
import os
from dotenv import load_dotenv

from models import db, User
from config import config_by_name

# Initialize extensions
mail = Mail()
login_manager = LoginManager()

def create_app(config_name='dev'):
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize plugins
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.habits import habits_bp
    from blueprints.api import api_bp
    from blueprints.profile import profile_bp
    from blueprints.social import social_bp
    from blueprints.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(social_bp, url_prefix='/friends')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Initialize Scheduler
    from scheduler import start_scheduler
    start_scheduler(app)
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'dev'))
    with app.app_context():
        db.create_all()
    app.run(debug=True)
