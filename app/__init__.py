from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import logging

def create_app():
    # Load environment variables from .env file
    load_dotenv()
    
    app = Flask(__name__)
    
    # 🔥 FIX: Session should not persist after browser close
    app.config['SESSION_PERMANENT'] = False

    # Configure secret key for session management
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
    
    # Configure session
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV', 'development') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = int(os.getenv('SESSION_TIMEOUT_MINUTES', 30)) * 60
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'error'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.db import get_user_by_id
        from app.routes.auth import User
        user_data = get_user_by_id(int(user_id))
        if user_data:
            return User(
                user_id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                role=user_data.get('role', 'user')
            )
        return None
    
    # Initialize logging
    from app.utils.logging_config import setup_logging
    setup_logging()
    
    # Needs to be imported inside or after app context loads env
    from app.models.db import init_db, ensure_default_admin
    
    with app.app_context():
        try:
            init_db()
            ensure_default_admin()
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")

    # Register blueprints
    from app.routes.views import views_bp
    from app.routes.api import api_bp
    from app.routes.auth import auth_bp
    
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    
    # Initialize scheduler if enabled
    if os.getenv('SCHEDULER_ENABLED', 'true').lower() == 'true':
        try:
            from app.services.scheduler import start_scheduler
            start_scheduler()
            logging.info("Attendance scheduler started")
        except Exception as e:
            logging.error(f"Failed to start scheduler: {e}")

    return app