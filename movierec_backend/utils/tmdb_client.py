import requests
import time
import logging
from django.conf import settings
from .exceptions import ExternalAPIException, RateLimitAPIException, AuthenticationAPIException

logger = logging.getLogger(__name__)

class TMDbClient:
    """
    Enhanced TMDB API client with robust error handling, retry logic, and monitoring.
    
    Features:
    - Automatic retry with exponential backoff
    - Comprehensive error handling for different HTTP status codes
    - Request/response logging for monitoring
    - Session management for efficient connections
    - Input validation and sanitization
    - Configurable timeouts and retry settings
    """
    BASE_URL = 'https://api.themoviedb.org/3'
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    TIMEOUT = 10  # seconds

    def __init__(self):
        self.api_key = getattr(settings, 'TMDB_API_KEY', None)
        if not self.api_key:
            raise AuthenticationAPIException("TMDB API key not configured")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MovieRecommendationBackend/1.0',
            'Accept': 'application/json'
        })

    def _handle_response(self, response, endpoint):
        """Handle different response status codes and raise appropriate exceptions"""
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 401:
            logger.error(f"TMDB API authentication failed for endpoint: {endpoint}")
            raise AuthenticationAPIException("TMDB API authentication failed")
        
        elif response.status_code == 403:
            logger.error(f"TMDB API access forbidden for endpoint: {endpoint}")
            raise AuthenticationAPIException("TMDB API access forbidden")
        
        elif response.status_code == 404:
            logger.warning(f"TMDB API resource not found: {endpoint}")
            raise ExternalAPIException("Movie not found", status_code=404, error_code="MOVIE_NOT_FOUND")
        
        elif response.status_code == 429:
            logger.warning(f"TMDB API rate limit exceeded for endpoint: {endpoint}")
            raise RateLimitAPIException("TMDB API rate limit exceeded")
        
        elif response.status_code >= 500:
            logger.error(f"TMDB API server error {response.status_code} for endpoint: {endpoint}")
            raise ExternalAPIException(f"TMDB API server error: {response.status_code}")
        
        else:
            logger.error(f"TMDB API unexpected error {response.status_code} for endpoint: {endpoint}")
            raise ExternalAPIException(f"TMDB API error: {response.status_code}")

    def _make_request(self, endpoint, params=None, retry_count=0):
        """Make HTTP request with retry logic and comprehensive error handling"""
        url = f"{self.BASE_URL}/{endpoint}"
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        try:
            logger.debug(f"Making request to TMDB API: {endpoint}")
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.TIMEOUT
            )
            return self._handle_response(response, endpoint)
            
        except requests.exceptions.Timeout:
            logger.warning(f"TMDB API timeout for endpoint: {endpoint}")
            if retry_count < self.MAX_RETRIES:
                time.sleep(self.RETRY_DELAY * (2 ** retry_count))  # Exponential backoff
                return self._make_request(endpoint, params, retry_count + 1)
            raise ExternalAPIException("TMDB API request timeout")
            
        except requests.exceptions.ConnectionError:
            logger.error(f"TMDB API connection error for endpoint: {endpoint}")
            if retry_count < self.MAX_RETRIES:
                time.sleep(self.RETRY_DELAY * (2 ** retry_count))
                return self._make_request(endpoint, params, retry_count + 1)
            raise ExternalAPIException("TMDB API connection failed")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDB API request error for endpoint {endpoint}: {str(e)}")
            raise ExternalAPIException(f"TMDB API request failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error in TMDB API request for endpoint {endpoint}: {str(e)}")
            raise ExternalAPIException(f"Unexpected error: {str(e)}")

    def get_trending_movies(self, time_window='day', page=1):
        """Get trending movies with comprehensive error handling and input validation"""
        if time_window not in ['day', 'week']:
            raise ValueError("time_window must be 'day' or 'week'")
        if page < 1:
            raise ValueError("page must be greater than 0")
        
        try:
            return self._make_request(f"trending/movie/{time_window}", params={'page': page})
        except Exception as e:
            logger.error(f"Error fetching trending movies: {str(e)}")
            raise

    def get_movie_details(self, movie_id):
        """Get movie details with comprehensive error handling and input validation"""
        if not movie_id or not str(movie_id).isdigit():
            raise ValueError("movie_id must be a valid integer")
        
        try:
            return self._make_request(f"movie/{movie_id}")
        except Exception as e:
            logger.error(f"Error fetching movie details for ID {movie_id}: {str(e)}")
            raise

    def search_movies(self, query, page=1):
        """Search movies with comprehensive error handling and input validation"""
        if not query or not query.strip():
            raise ValueError("query cannot be empty")
        if page < 1:
            raise ValueError("page must be greater than 0")
        
        try:
            return self._make_request("search/movie", params={'query': query.strip(), 'page': page})
        except Exception as e:
            logger.error(f"Error searching movies for query '{query}': {str(e)}")
            raise

    def get_movie_recommendations(self, movie_id, page=1):
        """Get movie recommendations with comprehensive error handling and input validation"""
        if not movie_id or not str(movie_id).isdigit():
            raise ValueError("movie_id must be a valid integer")
        if page < 1:
            raise ValueError("page must be greater than 0")
        
        try:
            return self._make_request(f"movie/{movie_id}/recommendations", params={'page': page})
        except Exception as e:
            logger.error(f"Error fetching movie recommendations for ID {movie_id}: {str(e)}")
            raise

    def get_popular_movies(self, page=1):
        """Get popular movies with comprehensive error handling and input validation"""
        if page < 1:
            raise ValueError("page must be greater than 0")
        
        try:
            return self._make_request("movie/popular", params={'page': page})
        except Exception as e:
            logger.error(f"Error fetching popular movies: {str(e)}")
            raise

    def __del__(self):
        """Clean up session on object destruction"""
        if hasattr(self, 'session'):
            self.session.close()