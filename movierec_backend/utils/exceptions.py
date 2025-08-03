import logging

logger = logging.getLogger(__name__)

class APIException(Exception):
    """Base exception for API errors - provides consistent error handling across the application"""
    def __init__(self, message="An error occurred", status_code=500, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class ExternalAPIException(APIException):
    """Exception for external API errors (like TMDB, payment gateways, etc.)"""
    def __init__(self, message="External API error", status_code=502, error_code="EXTERNAL_API_ERROR"):
        super().__init__(message, status_code, error_code)

class ValidationAPIException(APIException):
    """Exception for input validation errors - ensures consistent validation across all endpoints"""
    def __init__(self, message="Validation error", status_code=400, error_code="VALIDATION_ERROR"):
        super().__init__(message, status_code, error_code)

class AuthenticationAPIException(APIException):
    """Exception for authentication and authorization failures"""
    def __init__(self, message="Authentication failed", status_code=401, error_code="AUTHENTICATION_ERROR"):
        super().__init__(message, status_code, error_code)

class RateLimitAPIException(APIException):
    """Exception for rate limiting and throttling scenarios"""
    def __init__(self, message="Rate limit exceeded", status_code=429, error_code="RATE_LIMIT_ERROR"):
        super().__init__(message, status_code, error_code)

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF - provides consistent error responses across all API endpoints
    """
    # Import DRF components here to avoid circular imports
    try:
        from rest_framework.views import exception_handler
        from rest_framework.response import Response
        from rest_framework import status
        from django.core.exceptions import ValidationError
        from django.http import Http404
    except ImportError:
        # If DRF is not available, return None to use default handler
        return None
    
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the error response format
        error_data = {
            'error': {
                'message': response.data.get('detail', str(exc)),
                'code': getattr(exc, 'error_code', 'UNKNOWN_ERROR'),
                'status_code': response.status_code
            }
        }
        response.data = error_data
        return response
    
    # Handle custom exceptions
    if isinstance(exc, APIException):
        error_data = {
            'error': {
                'message': exc.message,
                'code': exc.error_code,
                'status_code': exc.status_code
            }
        }
        return Response(error_data, status=exc.status_code)
    
    # Handle Django exceptions
    if isinstance(exc, ValidationError):
        error_data = {
            'error': {
                'message': 'Validation error',
                'code': 'VALIDATION_ERROR',
                'status_code': 400,
                'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            }
        }
        return Response(error_data, status=400)
    
    if isinstance(exc, Http404):
        error_data = {
            'error': {
                'message': 'Resource not found',
                'code': 'NOT_FOUND',
                'status_code': 404
            }
        }
        return Response(error_data, status=404)
    
    # Log unexpected errors
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    # Return generic error for unexpected exceptions
    error_data = {
        'error': {
            'message': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'status_code': 500
        }
    }
    return Response(error_data, status=500) 