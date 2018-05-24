import os

from flask import Flask, jsonify
from flask_migrate import Migrate
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

try:
    from config import app_configuration
except ImportError:
    from bank_application_api.config import app_configuration

# function that creates the flask app, initializes the db and sets the routes
def create_flask_app(environment):
    app = Flask(__name__)
    app.config.from_object(app_configuration[environment])
    app.config['BUNDLE_ERRORS'] = True

    try:
        from api import models
    except ImportError:
        from bank_application_api.api import models

    # initialize SQLAlchemy
    models.db.init_app(app)

    # initilize migration commands
    migrate = Migrate(app, models.db)

    environment = os.getenv('FLASK_CONFIG')

    # Landing route
    @app.route('/')
    def index():
        return "Welcome to the Banking Application Api"

    # handle default 404 exceptions with a custom response
    @app.errorhandler(404)
    def resource_not_found(error):
        response = jsonify(dict(status='fail', data={
                    'error':'Not found', 
                    'message':'The requested URL was not found on the server.'
                }))
        response.status_code = 404
        return response

    # handle default 500 exceptions with a custom response
    @app.errorhandler(500)
    def internal_server_error(error):
        response = jsonify(dict(status=error, data={
                    'error':'Internal Server Error', 
                    'message':'The server encountered an internal error and was unable to complete your request.'
                }))
        response.status_code = 500
        return response

    return app

# creates the flask application
app = create_flask_app(os.getenv('FLASK_CONFIG'))

# starts the flask application
if __name__ == "__main__":
    app.run()
