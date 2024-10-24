from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from app.config import Config
from flask_migrate import Migrate  # Importer Flask-Migrate


# Initialisation des extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate() 

# Configuration de Flask-Login pour rediriger vers la page de login si un utilisateur non connecté tente d'accéder à une page protégée
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'  # Message Flash pour les utilisateurs non connectés

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation des extensions avec l'application Flask
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Importer et enregistrer le blueprint 'main'
    from app.routes import main
    app.register_blueprint(main)

    # Importer et enregistrer le blueprint 'admin'
    from app.routes import admin
    app.register_blueprint(admin)

    
    # Charger l'utilisateur avec Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
