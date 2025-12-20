"""
Application factory pattern for Flask
This module provides functions to initialize and configure the Flask application
"""
from flask import Flask, jsonify, make_response
from flask_restful import Api
# CORS is now handled by our custom middleware, not Flask-CORS
import logging
from logging.handlers import RotatingFileHandler
import os
from config import Config
from celery import Celery

def make_celery(app):
    """Create and configure Celery instance"""
    celery = Celery(
        app.import_name,
        backend=app.config.get('result_backend', 'redis://localhost:6379/0'),
        broker=app.config.get('broker_url', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
                
    celery.Task = ContextTask
    return celery

# Initialize Celery (will be configured in create_app)
celery = None

def create_app(config_class=Config):
    """Creates and configures the Flask application"""
    global celery
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure CORS using our custom middleware
    from app.api.cors_middleware import configure_cors
    configure_cors(app)
    
    # Note: We've removed Flask-CORS to prevent duplicate headers

    # Configure Celery
    celery = make_celery(app)
    
    # Register API blueprint
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix=app.config.get('API_PREFIX', '/api'))

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({"error": "Not found"}), 404)    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/ibov_api.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Zomma Quant API startup')

    return app, celery  # Return both app and celery

# Import tasks at the end to avoid circular imports
from app import tasks