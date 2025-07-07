"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""

from flask import Flask
from flask_talisman import Talisman
from flask_cors import CORS
from service import config
from service import models
import os
import sys
from service.common import log_handlers
from service import routes


# Create Flask application
app = Flask(__name__)
app.config.from_object(config)

from service.routes import bp  # no circular import because bp != app
app.register_blueprint(bp)

if os.getenv("TESTING", "False") == "True":
    app.config["TESTING"] = True

talisman = Talisman(app)
CORS(app)
if app.config.get("TESTING", False):
    talisman.force_https = False

# pylint: disable=wrong-import-position
from service.common import error_handlers, cli_commands  # noqa: F401 E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    models.init_db(app)  # make our database tables
except Exception as error:  # pylint: disable=broad-except
    app.logger.critical("%s: Cannot continue", error)
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info("Service initialized!")
