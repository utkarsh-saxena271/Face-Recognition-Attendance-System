from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import logging
from datetime import timedelta


def create_app():
    # Load environment variables
    load_dotenv()

    app = Flask(__name__)

    # ==============================
    # 🔐 SECURITY & SESSION CONFIG
    # ==============================
    secret = os.getenv('SECRET_KEY')
    if not secret:
        raise ValueError("SECRET_KEY not set in environment")
    app.config['SECRET_KEY'] = secret

    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
        minutes=int(os.getenv('SESSION_TIMEOUT_MINUTES', 30))
    )

    # ==============================
    # 🔑 LOGIN MANAGER
    # ==============================
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'error'

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

    # ==============================
    # 📝 LOGGING SETUP
    # ==============================
    from app.utils.logging_config import setup_logging
    setup_logging()

    # ==============================
    # 🗄️ DATABASE INIT
    # ==============================
    from app.models.db import init_db, ensure_default_admin

    with app.app_context():
        try:
            init_db()
            ensure_default_admin()
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")

    # ==============================
    # 🚀 🔥 DEEPFACE PRELOAD (KEY FIX)
    # ==============================
    try:
        from deepface import DeepFace
        import numpy as np

        print("🔥 Loading FaceNet model at startup...")

        # load model once
        DeepFace.build_model("Facenet")

        # warmup run (VERY IMPORTANT)
        dummy = np.zeros((224, 224, 3), dtype=np.uint8)
        DeepFace.represent(
            img_path=dummy,
            model_name="Facenet",
            enforce_detection=False,
            detector_backend="opencv"
        )

        print("✅ Face model fully ready (no delay now)")

    except Exception as e:
        logging.error(f"DeepFace preload failed: {e}")

    # ==============================
    # 📦 REGISTER BLUEPRINTS
    # ==============================
    from app.routes.views import views_bp
    from app.routes.api import api_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    # ==============================
    # ⏰ SCHEDULER (SAFE START)
    # ==============================
    if os.getenv('SCHEDULER_ENABLED', 'true').lower() == 'true':
        try:
            from app.services.scheduler import start_scheduler, scheduler

            # prevent duplicate scheduler (important for production)
            if os.getenv("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
                if not scheduler.running:
                    start_scheduler()
                    logging.info("Attendance scheduler started")

        except Exception as e:
            logging.error(f"Scheduler failed: {e}")

    return app