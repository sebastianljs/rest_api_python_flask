from flask import Flask
from flask_mongoengine import MongoEngine
from pets_api.store.views import store_app
from pets_api.home.views import home_app
from pet.views import pet_app
from pets_api.app.views import app_app
from pets_api.settings import MONGODB_HOST

db = MongoEngine()


def create_app(**config_overrides):
    app = Flask(__name__)
    app.config.from_pyfile("settings.py")
    app.config.update(config_overrides)
    db.init_app(app)

    # register blueprints
    app.register_blueprint(store_app)
    app.register_blueprint(home_app)
    app.register_blueprint(pet_app)
    app.register_blueprint(app_app)

    return app

def fixtures(test_db, collection, fixture):
    command = "mongoimport -h %s \
        -d %s \
        -c %s \
        < %s" % (MONGODB_HOST, test_db, collection, fixture)
    call(command, shell=True)