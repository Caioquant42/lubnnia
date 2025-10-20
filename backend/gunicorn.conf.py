# Gunicorn configuration file for ZommaQuant backend
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" in %(D)sµs'

# Process naming
proc_name = 'zommaquant_backend'

# Server mechanics
daemon = False
# pidfile = '/var/run/gunicorn/zommaquant_backend.pid'  # Commented out - systemd handles this
# user = 'www-data'  # Commented out - set in systemd service
# group = 'www-data'  # Commented out - set in systemd service
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Application module and callable is specified in the command line
# For example: gunicorn --config gunicorn.conf.py run:app

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'PYTHONPATH=/var/www/next/next2/project_mvp/backend',
]

# Preload application for better performance and memory usage
preload_app = True

# Enable stats if needed
# Enable this for monitoring
# statsd_host = 'localhost:8125' 