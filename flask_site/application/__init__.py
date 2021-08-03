import os

from flask import Flask
from flask_ngrok import run_with_ngrok

from .application import update_maps


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'database.db'),
        UPLOAD_FOLDER=os.path.join(app.root_path, 'application', 'maps'),
        ALLOWED_EXTENSIONS={'.csv'},
        FLASK_ENV='development'
    )
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.after_request
    def after_request(response):
        """Disable caching"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import application
    app.register_blueprint(application.bp)

    with app.app_context():
        update_maps()

    run_with_ngrok(app)

    return app
