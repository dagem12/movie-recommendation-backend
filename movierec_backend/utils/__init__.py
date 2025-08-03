# Utils app for movie recommendation backend
# Contains reusable utilities, external API clients, error handling, and framework-wide helpers

# Note: Imports are moved to individual modules to avoid circular import issues
# during Django app loading. Import these components directly from their modules.

# Available components:
# - Error handling: Custom exceptions, decorators, middleware
# - External APIs: TMDB client with retry logic and error handling
# - Validation: Input validation decorators and utilities
# - Logging: Request/response logging and monitoring
# - Caching: Response caching utilities (placeholder)
# - Rate limiting: Basic rate limiting utilities (placeholder)

# Example usage:
# from utils.exceptions import APIException, ValidationAPIException
# from utils.tmdb_client import TMDbClient
# from utils.decorators import handle_api_errors, log_api_call, validate_required_params
# from utils.middleware import RequestLoggingMiddleware, ErrorHandlingMiddleware
