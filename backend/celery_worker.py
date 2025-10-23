from app import create_app
from celerybeat_schedule import beat_schedule

# Create Flask app and get celery instance
flask_app, celery_app = create_app()

# Additional celery configuration
celery_app.conf.update(
    broker_url=flask_app.config.get('broker_url', 'redis://localhost:6379/0'),
    result_backend=flask_app.config.get('result_backend', 'redis://localhost:6379/0'),
    beat_schedule=beat_schedule,
    timezone=flask_app.config.get('timezone', 'America/Sao_Paulo'),
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_routes={
        'app.tasks.*': {'queue': 'default'},
    }
)

# Debug print statements
print("Flask app config loaded")
print("Celery Broker URL:", celery_app.conf.broker_url)
print("Celery Result Backend:", celery_app.conf.result_backend)
print("Beat Schedule loaded:", len(celery_app.conf.beat_schedule) if celery_app.conf.beat_schedule else 0, "tasks")
print("Timezone:", celery_app.conf.timezone)

# Export celery app for the services
celery = celery_app

# Make sure you're only exporting the celery app
if __name__ == '__main__':
    celery.start()