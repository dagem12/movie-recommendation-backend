import logging

logger = logging.getLogger(__name__)

# Import DRF components conditionally to avoid circular imports
try:
    from rest_framework.decorators import api_view, permission_classes
    from rest_framework.permissions import AllowAny
    from rest_framework.response import Response
    from rest_framework import status
    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False
    logger.warning("Django REST Framework not available. API views will not work.")

# Import our components conditionally
try:
    from .tmdb_client import TMDbClient
    from .exceptions import ExternalAPIException, ValidationAPIException
    from .decorators import handle_api_errors, validate_required_params, log_api_call
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    logger.warning("Utils components not available. API views will not work.")

if DRF_AVAILABLE and UTILS_AVAILABLE:
    @api_view(['GET'])
    @permission_classes([AllowAny])
    @handle_api_errors
    @log_api_call
    def get_trending_movies(request):
        """
        Get trending movies from TMDB API with error handling
        """
        try:
            time_window = request.GET.get('time_window', 'day')
            if time_window not in ['day', 'week']:
                raise ValidationAPIException("time_window must be 'day' or 'week'")
            
            client = TMDbClient()
            movies = client.get_trending_movies(time_window)
            
            return Response({
                'success': True,
                'data': movies,
                'time_window': time_window
            })
            
        except ExternalAPIException as e:
            logger.error(f"External API error in get_trending_movies: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': e.error_code,
                    'status_code': e.status_code
                }
            }, status=e.status_code)
        
        except Exception as e:
            logger.error(f"Unexpected error in get_trending_movies: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)

    @api_view(['GET'])
    @permission_classes([AllowAny])
    @handle_api_errors
    @log_api_call
    @validate_required_params(['query'])
    def search_movies(request):
        """
        Search movies with error handling and parameter validation
        """
        try:
            query = request.GET.get('query', '').strip()
            if not query:
                raise ValidationAPIException("Query parameter cannot be empty")
            
            page = int(request.GET.get('page', 1))
            if page < 1:
                raise ValidationAPIException("Page must be greater than 0")
            
            client = TMDbClient()
            results = client.search_movies(query)
            
            return Response({
                'success': True,
                'data': results,
                'query': query,
                'page': page
            })
            
        except ValueError as e:
            logger.warning(f"Validation error in search_movies: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'VALIDATION_ERROR',
                    'status_code': 400
                }
            }, status=400)
        
        except ExternalAPIException as e:
            logger.error(f"External API error in search_movies: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': e.error_code,
                    'status_code': e.status_code
                }
            }, status=e.status_code)
        
        except Exception as e:
            logger.error(f"Unexpected error in search_movies: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)

    @api_view(['GET'])
    @permission_classes([AllowAny])
    @handle_api_errors
    @log_api_call
    def get_movie_details(request, movie_id):
        """
        Get movie details with error handling
        """
        try:
            if not movie_id or not str(movie_id).isdigit():
                raise ValidationAPIException("Movie ID must be a valid integer")
            
            client = TMDbClient()
            movie = client.get_movie_details(movie_id)
            
            return Response({
                'success': True,
                'data': movie
            })
            
        except ValidationAPIException as e:
            logger.warning(f"Validation error in get_movie_details: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'VALIDATION_ERROR',
                    'status_code': 400
                }
            }, status=400)
        
        except ExternalAPIException as e:
            logger.error(f"External API error in get_movie_details: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': e.error_code,
                    'status_code': e.status_code
                }
            }, status=e.status_code)
        
        except Exception as e:
            logger.error(f"Unexpected error in get_movie_details: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)

    @api_view(['GET'])
    @permission_classes([AllowAny])
    @handle_api_errors
    @log_api_call
    def get_movie_recommendations(request, movie_id):
        """
        Get movie recommendations with error handling
        """
        try:
            if not movie_id or not str(movie_id).isdigit():
                raise ValidationAPIException("Movie ID must be a valid integer")
            
            client = TMDbClient()
            recommendations = client.get_movie_recommendations(movie_id)
            
            return Response({
                'success': True,
                'data': recommendations
            })
            
        except ValidationAPIException as e:
            logger.warning(f"Validation error in get_movie_recommendations: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'VALIDATION_ERROR',
                    'status_code': 400
                }
            }, status=400)
        
        except ExternalAPIException as e:
            logger.error(f"External API error in get_movie_recommendations: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': e.error_code,
                    'status_code': e.status_code
                }
            }, status=e.status_code)
        
        except Exception as e:
            logger.error(f"Unexpected error in get_movie_recommendations: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)

    @api_view(['GET'])
    @permission_classes([AllowAny])
    @handle_api_errors
    @log_api_call
    def get_popular_movies(request):
        """
        Get popular movies with error handling
        """
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                raise ValidationAPIException("Page must be greater than 0")
            
            client = TMDbClient()
            movies = client.get_popular_movies(page)
            
            return Response({
                'success': True,
                'data': movies,
                'page': page
            })
            
        except ValueError as e:
            logger.warning(f"Validation error in get_popular_movies: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'VALIDATION_ERROR',
                    'status_code': 400
                }
            }, status=400)
        
        except ExternalAPIException as e:
            logger.error(f"External API error in get_popular_movies: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'message': str(e),
                    'code': e.error_code,
                    'status_code': e.status_code
                }
            }, status=e.status_code)
        
        except Exception as e:
            logger.error(f"Unexpected error in get_popular_movies: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred',
                    'code': 'INTERNAL_ERROR',
                    'status_code': 500
                }
            }, status=500)

else:
    # Placeholder functions when DRF or utils are not available
    def get_trending_movies(request):
        return None
    
    def search_movies(request):
        return None
    
    def get_movie_details(request, movie_id):
        return None
    
    def get_movie_recommendations(request, movie_id):
        return None
    
    def get_popular_movies(request):
        return None
