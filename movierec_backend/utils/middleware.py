import time
import logging
import json

logger = logging.getLogger(__name__)

# Import Django components conditionally to avoid circular imports
try:
    from django.utils.deprecation import MiddlewareMixin
    from django.http import JsonResponse
    from .exceptions import APIException
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    logger.warning("Django components not available. Middleware will not work.")

if DJANGO_AVAILABLE:
    class RequestLoggingMiddleware(MiddlewareMixin):
        """Middleware to log all API requests and responses"""
        
        def process_request(self, request):
            request.start_time = time.time()
            
            # Log request details
            log_data = {
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                'ip': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
            
            logger.info(f"API Request: {json.dumps(log_data)}")
            return None
        
        def process_response(self, request, response):
            if hasattr(request, 'start_time'):
                duration = time.time() - request.start_time
                
                # Log response details
                log_data = {
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': round(duration, 3),
                    'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                }
                
                if response.status_code >= 400:
                    logger.warning(f"API Response Error: {json.dumps(log_data)}")
                else:
                    logger.info(f"API Response: {json.dumps(log_data)}")
            
            return response
        
        def process_exception(self, request, exception):
            if hasattr(request, 'start_time'):
                duration = time.time() - request.start_time
                
                # Log exception details
                log_data = {
                    'method': request.method,
                    'path': request.path,
                    'exception_type': type(exception).__name__,
                    'exception_message': str(exception),
                    'duration': round(duration, 3),
                    'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                }
                
                logger.error(f"API Exception: {json.dumps(log_data)}", exc_info=True)
            
            return None
        
        def _get_client_ip(self, request):
            """Extract client IP address from request"""
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip

    class ErrorHandlingMiddleware(MiddlewareMixin):
        """Middleware to handle unhandled exceptions and provide consistent error responses"""
        
        def process_exception(self, request, exception):
            """Handle unhandled exceptions and return consistent error responses"""
            
            # Don't handle exceptions for non-API endpoints
            if not request.path.startswith('/api/'):
                return None
            
            # Handle custom API exceptions
            if isinstance(exception, APIException):
                return JsonResponse({
                    'error': {
                        'message': exception.message,
                        'code': exception.error_code,
                        'status_code': exception.status_code
                    }
                }, status=exception.status_code)
            
            # Handle common Django exceptions
            if hasattr(exception, '__class__'):
                exception_name = exception.__class__.__name__
                
                if exception_name == 'ValidationError':
                    return JsonResponse({
                        'error': {
                            'message': 'Validation error',
                            'code': 'VALIDATION_ERROR',
                            'status_code': 400,
                            'details': str(exception)
                        }
                    }, status=400)
                
                elif exception_name == 'DoesNotExist':
                    return JsonResponse({
                        'error': {
                            'message': 'Resource not found',
                            'code': 'NOT_FOUND',
                            'status_code': 404
                        }
                    }, status=404)
                
                elif exception_name == 'PermissionDenied':
                    return JsonResponse({
                        'error': {
                            'message': 'Permission denied',
                            'code': 'PERMISSION_DENIED',
                            'status_code': 403
                        }
                    }, status=403)
            
            # Log unexpected exceptions
            logger.error(f"Unhandled exception in API: {type(exception).__name__}: {str(exception)}", 
                        exc_info=True)
            
            # Return generic error response
            return JsonResponse({
                'error': {
                    'message': 'Internal server error',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)

else:
    # Placeholder classes when Django is not available
    class RequestLoggingMiddleware:
        def __init__(self, get_response=None):
            self.get_response = get_response
        
        def __call__(self, request):
            return self.get_response(request) if self.get_response else None
    
    class ErrorHandlingMiddleware:
        def __init__(self, get_response=None):
            self.get_response = get_response
        
        def __call__(self, request):
            return self.get_response(request) if self.get_response else None 