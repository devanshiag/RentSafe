from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_mail import Mail

from .config import Config


# Initialize extensions (without app)
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'resident_login'
login_manager.login_message_category = 'info'
mail = Mail()

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Log application startup
    app.logger.info("Application startup")

    # Import and register routes/models
    from app.routes.main import main
    from app.routes.admin import admin
    from app.routes.resident import resident

    app.register_blueprint(main)
    app.register_blueprint(resident)
    app.register_blueprint(admin)



    return app

