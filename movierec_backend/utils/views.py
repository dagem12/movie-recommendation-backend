from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from utils.cache_service import cache_service
from utils.decorators import handle_api_errors, log_api_call
import logging

logger = logging.getLogger(__name__)

class CacheManagementView(APIView):
    """
    Cache management endpoint for monitoring and administration
    
    Features:
    - Get cache statistics
    - Clear all caches (admin only)
    - Monitor cache performance
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @handle_api_errors
    @log_api_call
    def get(self, request):
        """Get cache statistics"""
        try:
            stats = cache_service.get_cache_stats()
            return Response({
                'success': True,
                'data': stats
            })
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to get cache statistics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @handle_api_errors
    @log_api_call
    def delete(self, request):
        """Clear all caches (admin only)"""
        try:
            success = cache_service.clear_all_caches()
            if success:
                return Response({
                    'success': True,
                    'message': 'All caches cleared successfully'
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Failed to clear caches'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error clearing caches: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to clear caches'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
