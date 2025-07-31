import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up file handler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    
    # Set up formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Set up application logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Log application startup
    app.logger.info('Application startup')
    
    return app
