from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from config import Config
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    
    # Login settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'info'
    
    # Create upload folder if not exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Register blueprints (routes)
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.courses import courses_bp
    from app.routes.notes import notes_bp
    from app.routes.admin import admin_bp
    from app.routes.notifications import notifications_bp
    from app.routes.chat import chat_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(notes_bp, url_prefix='/notes')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

