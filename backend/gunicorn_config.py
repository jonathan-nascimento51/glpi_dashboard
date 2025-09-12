"""
Gunicorn configuration for production-quality benchmark testing
"""

import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 4  # multiprocessing.cpu_count()
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 5

# Restart workers after this many requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "warning"

# Process naming
proc_name = "glpi_dashboard_backend"

# Performance tuning
preload_app = True  # Load application code before the worker processes are forked
enable_stdio_inheritance = True

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190