from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth
    from app.routes.records import records
    from app.routes.dashboard import dashboard

    app.register_blueprint(auth)
    app.register_blueprint(records)
    app.register_blueprint(dashboard)

    with app.app_context():
        db.create_all()

    return app
