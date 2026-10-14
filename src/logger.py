import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
from flask import request, g

LOG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def get_log_level():
    level_name = os.environ.get('LOG_LEVEL', 'INFO').upper()
    return getattr(logging, level_name, logging.INFO)

def setup_root_logger():
    """Sets up the root logger with console and rotating file handlers."""
    log_level = get_log_level()
    root_logger = logging.getLogger()
    
    # Avoid duplicate handlers if already configured
    if root_logger.handlers:
        return root_logger

    root_logger.setLevel(log_level)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # 1. Console Handler (stdout for container logs / docker / k8s)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. Rotating File Handler (persisted on disk)
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'mathpuzzle.log'),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        console_handler.handle(
            logging.LogRecord(
                name='logger',
                level=logging.WARNING,
                pathname=__file__,
                lineno=46,
                msg=f"Could not create file log handler: {e}",
                args=(),
                exc_info=None
            )
        )

    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Returns a named logger configured with the standard system format."""
    setup_root_logger()
    return logging.getLogger(name)

def setup_app_logging(app):
    """Integrates request lifecycle and error logging with Flask app."""
    setup_root_logger()
    app.logger.handlers = logging.getLogger().handlers
    app.logger.setLevel(get_log_level())

    @app.before_request
    def log_request_start():
        g.request_start_time = time.time()
        # Skip static assets from noisy logs unless DEBUG
        if not request.path.startswith(('/static/', '/favicon.ico', '/sw.js')):
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            app.logger.info(f"--> {request.method} {request.path} from {client_ip}")

    @app.after_request
    def log_request_end(response):
        if hasattr(g, 'request_start_time'):
            duration_ms = (time.time() - g.request_start_time) * 1000
            if not request.path.startswith(('/static/', '/favicon.ico')):
                status = response.status_code
                log_msg = f"<-- {request.method} {request.path} status={status} duration={duration_ms:.1f}ms"
                if status >= 500:
                    app.logger.error(log_msg)
                elif status >= 400:
                    app.logger.warning(log_msg)
                else:
                    app.logger.info(log_msg)
        return response
