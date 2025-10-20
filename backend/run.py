from flask import Flask
from app.api import bp as api_bp
from app import create_app

app, celery = create_app()

if __name__ == '__main__':
    app.run(debug=True)