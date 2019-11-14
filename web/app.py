"""The app module, containing the app factory function."""
from flask import Flask, render_template
from web.extensions import db, migrate, mail
from web.settings import ProdConfig
from web.views import main
from web.exceptions import InvalidUsage

def create_app(config_object=ProdConfig, verbose=True, validate=True):
    if validate:
        config_object.validate()
    if verbose:
        config_object.verbose_config()

    """An application factory."""
    app = Flask(__name__.split('.')[0])
    app.url_map.strict_slashes = False
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app

def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(main)

def register_errorhandlers(app):
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        response = error.to_json()
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
