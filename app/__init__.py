from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .knowledge_base import bp as knowledge_base_blueprint
    app.register_blueprint(knowledge_base_blueprint, url_prefix='/knowledge_base')
    
    from .tickets import tickets as tickets_blueprint
    app.register_blueprint(tickets_blueprint, url_prefix='/tickets')
    
    from .it_assets import bp as it_assets_blueprint
    app.register_blueprint(it_assets_blueprint, url_prefix='/it_assets')
    
    from .users.views import bp as users_blueprint # Import the bp object from views
    app.register_blueprint(users_blueprint, url_prefix='/users') # Register the correct blueprint object

    return app