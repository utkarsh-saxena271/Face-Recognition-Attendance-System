import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging():
    """Configure logging for the application"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Log format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # File handler (DEBUG level) - General logs
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOG_DIR, 'application.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # File handler for attendance events
    attendance_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOG_DIR, 'attendance.log'),
        maxBytes=5242880,  # 5MB
        backupCount=10
    )
    attendance_handler.setLevel(logging.INFO)
    attendance_handler.setFormatter(log_format)
    
    attendance_logger = logging.getLogger('attendance')
    attendance_logger.addHandler(attendance_handler)
    
    # File handler for authentication events
    auth_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOG_DIR, 'auth.log'),
        maxBytes=5242880,  # 5MB
        backupCount=10
    )
    auth_handler.setLevel(logging.INFO)
    auth_handler.setFormatter(log_format)
    
    auth_logger = logging.getLogger('auth')
    auth_logger.addHandler(auth_handler)
    
    # File handler for errors
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOG_DIR, 'errors.log'),
        maxBytes=5242880,  # 5MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    root_logger.addHandler(error_handler)
    
    return {
        'root': root_logger,
        'attendance': attendance_logger,
        'auth': auth_logger
    }


# Module-level loggers
def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(name)
