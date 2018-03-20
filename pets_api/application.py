from flask import Flask
from flask_mongoengine import MongoEngine
from home.views import home_app

db = MongoEngine()


def create_app(**config_overrides):
    app = Flask(__name__)

    # Load config
    app.config.from_pyfile("settings.py")

    # Apply overrides for tests
    app.config.update(config_overrides)

    # Setup db
    db.init_app(app)

    # import blueprints
    app.register_blueprint(home_app)

    return app