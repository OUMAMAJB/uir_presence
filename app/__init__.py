from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_bcrypt import Bcrypt  # <-- AJOUT
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
bcrypt = Bcrypt()  # <-- AJOUT

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)  # <-- AJOUT

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Register Blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.routes.import_export import import_bp
    app.register_blueprint(import_bp, url_prefix='/admin')

    from app.routes.department import department_bp
    app.register_blueprint(department_bp, url_prefix='/department')

    from app.routes.track import track_bp
    app.register_blueprint(track_bp, url_prefix='/track')

    from app.routes.teacher import teacher_bp
    app.register_blueprint(teacher_bp, url_prefix='/teacher')

    from app.routes.student import student_bp
    app.register_blueprint(student_bp, url_prefix='/student')

    return app
