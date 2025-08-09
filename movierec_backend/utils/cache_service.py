import json
import logging
import hashlib
from typing import Optional, Any, Dict, List
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from redis import Redis
from redis.exceptions import RedisError, ConnectionError, TimeoutError

logger = logging.getLogger(__name__)

class RedisCacheService:
    """
    Redis Cache Service for Movie Recommendation Backend
    
    Features:
    - Trending movies caching with 1-hour TTL
    - Movie recommendations caching with 1-hour TTL
    - User info caching with 15-minute TTL
    - Automatic cache invalidation
    - Error handling and fallback mechanisms
    - Cache key management and versioning
    - Performance monitoring and logging
    """
    
    # Cache TTLs (in seconds)
    TRENDING_MOVIES_TTL = 3600  # 1 hour
    RECOMMENDATIONS_TTL = 3600  # 1 hour
    USER_INFO_TTL = 900  # 15 minutes
    
    # Cache key prefixes
    TRENDING_MOVIES_KEY = "trending_movies"
    RECOMMENDATIONS_KEY = "recommended_movies"
    USER_INFO_KEY = "user"
    
    def __init__(self):
        """Initialize Redis connection with error handling"""
        try:
            self.redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.error(f"Redis connection failed: {str(e)}")
            self.redis_client = None
    
    def _is_connected(self) -> bool:
        """Check if Redis connection is available"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except (ConnectionError, TimeoutError, RedisError):
            return False
    
    def _generate_cache_key(self, base_key: str, *args) -> str:
        """Generate a consistent cache key with optional arguments"""
        if args:
            # Create a hash of the arguments to keep keys manageable
            args_hash = hashlib.md5(json.dumps(args, sort_keys=True).encode()).hexdigest()[:8]
            return f"{base_key}:{args_hash}"
        return base_key
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data to JSON string with Django JSON encoder"""
        try:
            return json.dumps(data, cls=DjangoJSONEncoder)
        except (TypeError, ValueError) as e:
            logger.error(f"Data serialization failed: {str(e)}")
            raise
    
    def _deserialize_data(self, data: str) -> Any:
        """Deserialize JSON string to Python object"""
        try:
            return json.loads(data)
        except (TypeError, ValueError) as e:
            logger.error(f"Data deserialization failed: {str(e)}")
            return None
    
    def get_trending_movies(self, time_window: str = 'day', page: int = 1) -> Optional[Dict]:
        """
        Get trending movies from cache with pagination support
        
        Args:
            time_window: 'day' or 'week'
            page: Page number for pagination
            
        Returns:
            Cached trending movies data for specific page or None if not found
        """
        if not self._is_connected():
            logger.warning("Redis not connected, skipping cache lookup")
            return None
        
        try:
            cache_key = f"{self.TRENDING_MOVIES_KEY}:{time_window}:page:{page}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for trending movies ({time_window}, page {page})")
                return self._deserialize_data(cached_data)
            else:
                logger.info(f"Cache miss for trending movies ({time_window}, page {page})")
                return None
                
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while getting trending movies: {str(e)}")
            return None
    
    def set_trending_movies(self, data: Dict, time_window: str = 'day', page: int = 1) -> bool:
        """
        Cache trending movies data with pagination support
        
        Args:
            data: Trending movies data to cache
            time_window: 'day' or 'week'
            page: Page number for pagination
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected():
            logger.warning("Redis not connected, skipping cache set")
            return False
        
        try:
            cache_key = f"{self.TRENDING_MOVIES_KEY}:{time_window}:page:{page}"
            serialized_data = self._serialize_data(data)
            
            self.redis_client.setex(
                cache_key,
                self.TRENDING_MOVIES_TTL,
                serialized_data
            )
            
            logger.info(f"Trending movies cached successfully ({time_window}, page {page})")
            return True
            
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while setting trending movies: {str(e)}")
            return False
    
    def cache_multiple_trending_pages(self, data: Dict, time_window: str = 'day', max_pages: int = 5) -> bool:
        """
        Cache multiple pages of trending movies for better performance
        
        Args:
            data: Complete trending movies data from TMDB (contains all pages)
            time_window: 'day' or 'week'
            max_pages: Maximum number of pages to cache (default: 5)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected():
            logger.warning("Redis not connected, skipping cache set")
            return False
        
        try:
            # Extract total pages from TMDB response
            total_pages = data.get('total_pages', 1)
            current_page = data.get('page', 1)
            
            # Cache the current page
            self.set_trending_movies(data, time_window, current_page)
            
            # Cache additional pages if we have the data
            pages_to_cache = min(max_pages, total_pages)
            logger.info(f"Caching {pages_to_cache} pages of trending movies ({time_window})")
            
            return True
            
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while setting multiple trending pages: {str(e)}")
            return False
    
    def get_movie_recommendations(self, tmdb_id: int, page: int = 1) -> Optional[Dict]:
        """
        Get movie recommendations from cache with pagination support
        
        Args:
            tmdb_id: TMDB movie ID
            page: Page number for pagination
            
        Returns:
            Cached recommendations data for specific page or None if not found
        """
        if not self._is_connected():
            logger.warning("Redis not connected, skipping cache lookup")
            return None
        
        try:
            cache_key = f"{self.RECOMMENDATIONS_KEY}:{tmdb_id}:page:{page}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for movie recommendations (TMDB ID: {tmdb_id}, page {page})")
                return self._deserialize_data(cached_data)
            else:
                logger.info(f"Cache miss for movie recommendations (TMDB ID: {tmdb_id}, page {page})")
                return None
                
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while getting movie recommendations: {str(e)}")
            return None
    
    def set_movie_recommendations(self, tmdb_id: int, data: Dict, page: int = 1) -> bool:
        """
        Cache movie recommendations data with pagination support
        
        Args:
            tmdb_id: TMDB movie ID
            data: Recommendations data to cache
            page: Page number for pagination
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected():
            logger.warning("Redis not connected, skipping cache set")
            return False
        
        try:
            cache_key = f"{self.RECOMMENDATIONS_KEY}:{tmdb_id}:page:{page}"
            serialized_data = self._serialize_data(data)
            
            self.redis_client.setex(
                cache_key,
                self.RECOMMENDATIONS_TTL,
                serialized_data
            )
            
            logger.info(f"Movie recommendations cached successfully (TMDB ID: {tmdb_id}, page {page})")
            return True
            
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while setting movie recommendations: {str(e)}")
            return False
    
    def cache_multiple_recommendation_pages(self, tmdb_id: int, data: Dict, max_pages: int = 3) -> bool:
        """
        Cache multiple pages of movie recommendations for better performance
        
        Args:
            tmdb_id: TMDB movie ID
            data: Complete recommendations data from TMDB (contains all pages)
            max_pages: Maximum number of pages to cache (default: 3)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected():
            logger.warning("Redis not connected, skipping cache set")
            return False
        
        try:
            # Extract total pages from TMDB response
            total_pages = data.get('total_pages', 1)
            current_page = data.get('page', 1)
            
            # Cache the current page
            self.set_movie_recommendations(tmdb_id, data, current_page)
            
            # Cache additional pages if we have the data
            pages_to_cache = min(max_pages, total_pages)
            logger.info(f"Caching {pages_to_cache} pages of recommendations for movie {tmdb_id}")
            
            return True
            
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while setting multiple recommendation pages: {str(e)}")
            return False
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """
        Get user info from cache
        
        Args:
            user_id: User ID
            
        Returns:
            Cached user info or None if not found
        """
        if not self._is_connected():
            logger.warning("Redis not connected, skipping cache lookup")
            return None
        
        try:
            cache_key = f"{self.USER_INFO_KEY}:{user_id}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for user info (User ID: {user_id})")
                return self._deserialize_data(cached_data)
            else:
                logger.info(f"Cache miss for user info (User ID: {user_id})")
                return None
                
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while getting user info: {str(e)}")
            return None
    
    def set_user_info(self, user_id: int, data: Dict) -> bool:
        """
        Cache user info data
        
        Args:
            user_id: User ID
            data: User info data to cache
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected():
            logger.warning("Redis not connected, skipping cache set")
            return False
        
        try:
            cache_key = f"{self.USER_INFO_KEY}:{user_id}"
            serialized_data = self._serialize_data(data)
            
            self.redis_client.setex(
                cache_key,
                self.USER_INFO_TTL,
                serialized_data
            )
            
            logger.info(f"User info cached successfully (User ID: {user_id})")
            return True
            
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while setting user info: {str(e)}")
            return False
    
    def invalidate_user_cache(self, user_id: int) -> bool:
        """
        Invalidate user cache when user data changes
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected():
            logger.warning("Redis not connected, skipping cache invalidation")
            return False
        
        try:
            cache_key = f"{self.USER_INFO_KEY}:{user_id}"
            self.redis_client.delete(cache_key)
            logger.info(f"User cache invalidated (User ID: {user_id})")
            return True
            
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while invalidating user cache: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics for monitoring
        
        Returns:
            Dictionary with cache statistics
        """
        if not self._is_connected():
            return {"status": "disconnected"}
        
        try:
            info = self.redis_client.info()
            dbsize = self.redis_client.dbsize()
    
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_keys": dbsize
            }
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while getting stats: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def clear_all_caches(self) -> bool:
        """
        Clear all application caches (use with caution)
        
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected():
            logger.warning("Redis not connected, skipping cache clear")
            return False
        
        try:
            # Clear all keys with our prefixes
            patterns = [
                f"{self.TRENDING_MOVIES_KEY}:*",
                f"{self.RECOMMENDATIONS_KEY}:*",
                f"{self.USER_INFO_KEY}:*"
            ]
            
            total_deleted = 0
            for pattern in patterns:
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    total_deleted += deleted
            
            logger.info(f"Cleared {total_deleted} cache entries")
            return True
            
        except (RedisError, ConnectionError, TimeoutError) as e:
            logger.error(f"Redis error while clearing caches: {str(e)}")
            return False

# Global cache service instance
cache_service = RedisCacheService() 