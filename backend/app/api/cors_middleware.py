"""
CORS middleware for the Flask application
Handles Cross-Origin Resource Sharing settings
"""
from flask import request, current_app

def configure_cors(app):
    """
    Configure CORS settings for the Flask application
    
    This implementation is designed to work with Nginx which is already
    setting the CORS headers. Flask will not duplicate the headers but
    will handle any CORS logic not covered by Nginx.
    """
    @app.after_request
    def handle_cors(response):
        # Handle OPTIONS pre-flight requests properly
        if request.method == 'OPTIONS':
            response.status_code = 200
            # Let Nginx handle the CORS headers
            return response
            
        # Check if we're in a development environment without Nginx
        if app.debug and 'Access-Control-Allow-Origin' not in response.headers:
            # Get allowed origins from config
            allowed_origins = current_app.config.get('ALLOWED_ORIGINS', ['http://localhost:3000', 'https://zommaquant.com.br'])
            origin = request.headers.get('Origin')
            
            # For development without Nginx, set CORS headers
            if origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                # In debug mode, be permissive for local development
                response.headers['Access-Control-Allow-Origin'] = '*'
                
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight requests for 1 hour
        
        return response
        
    return app
