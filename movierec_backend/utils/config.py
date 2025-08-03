"""
Configuration settings for error handling and logging
"""

import os
from django.conf import settings

# Error handling configuration
ERROR_HANDLING_CONFIG = {
    'ENABLE_LOGGING': True,
    'LOG_LEVEL': 'INFO',
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 1,
    'TIMEOUT': 10,
    'ENABLE_RATE_LIMITING': True,
    'RATE_LIMIT_REQUESTS': 100,
    'RATE_LIMIT_WINDOW': 60,
}

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/api_errors.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/errors.log',
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'utils': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'utils.tmdb_client': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'utils.views': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

def get_error_handling_config():
    """Get error handling configuration with defaults"""
    config = ERROR_HANDLING_CONFIG.copy()
    
    # Override with Django settings if available
    if hasattr(settings, 'ERROR_HANDLING_CONFIG'):
        config.update(settings.ERROR_HANDLING_CONFIG)
    
    return config

def get_logging_config():
    """Get logging configuration with defaults"""
    config = LOGGING_CONFIG.copy()
    
    # Override with Django settings if available
    if hasattr(settings, 'LOGGING_CONFIG'):
        config.update(settings.LOGGING_CONFIG)
    
    return config

def setup_logging():
    """Setup logging configuration"""
    import logging.config
    
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Apply logging configuration
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)
    
    return logging_config 