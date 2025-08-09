from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.cache_service import cache_service
from utils.decorators import handle_api_errors, log_api_call
from .models import Settings
from .serializers import (
    SettingsSerializer, 
    SettingsListSerializer, 
    SettingsCreateSerializer, 
    SettingsUpdateSerializer
)
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
    
    @swagger_auto_schema(
        operation_description="Get cache statistics and performance metrics",
        operation_summary="Get Cache Statistics",
        operation_id="get_cache_stats",
        tags=["System Management"],
        responses={
            200: openapi.Response(
                description="Cache statistics retrieved successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "total_keys": 150,
                            "memory_usage": "2.5MB",
                            "hit_rate": 0.85,
                            "miss_rate": 0.15,
                            "total_requests": 1000,
                            "cache_hits": 850,
                            "cache_misses": 150
                        }
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Authentication credentials were not provided"
                    }
                }
            ),
            403: openapi.Response(
                description="Admin access required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "You do not have permission to perform this action"
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Failed to get cache statistics"
                    }
                }
            )
        }
    )
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
    
    @swagger_auto_schema(
        operation_description="Clear all caches (admin only). This will remove all cached data and may temporarily impact performance.",
        operation_summary="Clear All Caches",
        operation_id="clear_all_caches",
        tags=["System Management"],
        responses={
            200: openapi.Response(
                description="All caches cleared successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "All caches cleared successfully"
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Authentication credentials were not provided"
                    }
                }
            ),
            403: openapi.Response(
                description="Admin access required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "You do not have permission to perform this action"
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Failed to clear caches"
                    }
                }
            )
        }
    )
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


class SettingsListView(ListCreateAPIView):
    """
    Settings management endpoint.
    
    GET: List all settings (any authenticated user)
    POST: Create new setting (admin only)
    """
    permission_classes = [IsAuthenticated]
    queryset = Settings.objects.all()
    
    def get_serializer_class(self):
        """Use different serializers for GET and POST"""
        if self.request.method == 'POST':
            return SettingsCreateSerializer
        return SettingsListSerializer
    
    def get_permissions(self):
        """Admin required for POST, any authenticated user for GET"""
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="List all system settings. Accessible to any authenticated user.",
        operation_summary="List All Settings",
        operation_id="list_settings",
        tags=["System Management"],
        responses={
            200: openapi.Response(
                description="Settings list retrieved successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "data": [
                            {
                                "id": 1,
                                "setting_code": "theme_config",
                                "setting_value": {"primary_color": "#007bff", "dark_mode": True},
                                "description": "Frontend theme configuration",
                                "is_active": True,
                                "created_at": "2025-01-27T12:00:00Z",
                                "updated_at": "2025-01-27T12:00:00Z"
                            }
                        ]
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Authentication credentials were not provided"
                    }
                }
            )
        }
    )
    @handle_api_errors
    @log_api_call
    def get(self, request, *args, **kwargs):
        """List all settings"""
        try:
            settings = self.get_queryset()
            serializer = self.get_serializer(settings, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'count': settings.count()
            })
        except Exception as e:
            logger.error(f"Error listing settings: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to list settings'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Create a new system setting. Admin access required.",
        operation_summary="Create New Setting",
        operation_id="create_setting",
        tags=["System Management"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['setting_code', 'setting_value'],
            properties={
                'setting_code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Unique identifier for the setting (e.g., 'theme_config', 'api_limits')",
                    max_length=100
                ),
                'setting_value': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="JSON value for the setting configuration"
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Optional description of what this setting controls"
                ),
                'is_active': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Whether this setting is currently active",
                    default=True
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="Setting created successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "id": 2,
                            "setting_code": "api_limits",
                            "setting_value": {"max_requests": 1000, "timeout": 30},
                            "description": "API rate limiting configuration",
                            "is_active": True,
                            "created_at": "2025-01-27T12:00:00Z",
                            "updated_at": "2025-01-27T12:00:00Z"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "setting_code already exists"
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Authentication credentials were not provided"
                    }
                }
            ),
            403: openapi.Response(
                description="Admin access required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "You do not have permission to perform this action"
                    }
                }
            )
        }
    )
    @handle_api_errors
    @log_api_call
    def post(self, request, *args, **kwargs):
        """Create new setting (admin only)"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            setting = serializer.save()
            
            return Response({
                'success': True,
                'data': SettingsSerializer(setting).data,
                'message': 'Setting created successfully'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating setting: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to create setting'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SettingsDetailView(RetrieveUpdateDestroyAPIView):
    """
    Individual setting management endpoint.
    
    GET: Get setting details (any authenticated user)
    PUT/PATCH: Update setting (admin only)
    DELETE: Delete setting (admin only)
    """
    permission_classes = [IsAuthenticated]
    queryset = Settings.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """Use appropriate serializer based on method"""
        if self.request.method in ['PUT', 'PATCH']:
            return SettingsUpdateSerializer
        return SettingsSerializer
    
    def get_permissions(self):
        """Admin required for PUT/PATCH/DELETE, any authenticated user for GET"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="Get details of a specific setting by ID. Accessible to any authenticated user.",
        operation_summary="Get Setting Details",
        operation_id="get_setting_detail",
        tags=["System Management"],
        responses={
            200: openapi.Response(
                description="Setting details retrieved successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "setting_code": "theme_config",
                            "setting_value": {"primary_color": "#007bff", "dark_mode": True},
                            "description": "Frontend theme configuration",
                            "is_active": True,
                            "created_at": "2025-01-27T12:00:00Z",
                            "updated_at": "2025-01-27T12:00:00Z"
                        }
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Authentication credentials were not provided"
                    }
                }
            ),
            404: openapi.Response(
                description="Setting not found",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Setting not found"
                    }
                }
            )
        }
    )
    @handle_api_errors
    @log_api_call
    def get(self, request, *args, **kwargs):
        """Get setting details"""
        try:
            setting = self.get_object()
            serializer = SettingsSerializer(setting)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Exception as e:
            logger.error(f"Error getting setting details: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to get setting details'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Update a setting completely. Admin access required.",
        operation_summary="Update Setting (PUT)",
        operation_id="update_setting_put",
        tags=["System Management"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['setting_code', 'setting_value'],
            properties={
                'setting_code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Unique identifier for the setting",
                    max_length=100
                ),
                'setting_value': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="JSON value for the setting configuration"
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Description of what this setting controls"
                ),
                'is_active': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Whether this setting is currently active"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Setting updated successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "setting_code": "theme_config",
                            "setting_value": {"primary_color": "#28a745", "dark_mode": False},
                            "description": "Updated frontend theme configuration",
                            "is_active": True,
                            "created_at": "2025-01-27T12:00:00Z",
                            "updated_at": "2025-01-27T12:30:00Z"
                        },
                        "message": "Setting updated successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Invalid JSON data in setting_value"
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Authentication credentials were not provided"
                    }
                }
            ),
            403: openapi.Response(
                description="Admin access required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "You do not have permission to perform this action"
                    }
                }
            ),
            404: openapi.Response(
                description="Setting not found",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Setting not found"
                    }
                }
            )
        }
    )
    @handle_api_errors
    @log_api_call
    def put(self, request, *args, **kwargs):
        """Update setting completely (admin only)"""
        try:
            setting = self.get_object()
            serializer = SettingsUpdateSerializer(setting, data=request.data)
            serializer.is_valid(raise_exception=True)
            updated_setting = serializer.save()
            
            return Response({
                'success': True,
                'data': SettingsSerializer(updated_setting).data,
                'message': 'Setting updated successfully'
            })
        except Exception as e:
            logger.error(f"Error updating setting: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to update setting'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Partially update a setting. Admin access required.",
        operation_summary="Update Setting (PATCH)",
        operation_id="update_setting_patch",
        tags=["System Management"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'setting_value': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="JSON value for the setting configuration"
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Description of what this setting controls"
                ),
                'is_active': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Whether this setting is currently active"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Setting updated successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "setting_code": "theme_config",
                            "setting_value": {"primary_color": "#007bff", "dark_mode": True},
                            "description": "Frontend theme configuration",
                            "is_active": False,
                            "created_at": "2025-01-27T12:00:00Z",
                            "updated_at": "2025-01-27T12:45:00Z"
                        },
                        "message": "Setting updated successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Invalid JSON data in setting_value"
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Authentication credentials were not provided"
                    }
                }
            ),
            403: openapi.Response(
                description="Admin access required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "You do not have permission to perform this action"
                    }
                }
            ),
            404: openapi.Response(
                description="Setting not found",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Setting not found"
                    }
                }
            )
        }
    )
    @handle_api_errors
    @log_api_call
    def patch(self, request, *args, **kwargs):
        """Partially update setting (admin only)"""
        try:
            setting = self.get_object()
            serializer = SettingsUpdateSerializer(setting, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_setting = serializer.save()
            
            return Response({
                'success': True,
                'data': SettingsSerializer(updated_setting).data,
                'message': 'Setting updated successfully'
            })
        except Exception as e:
            logger.error(f"Error updating setting: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to update setting'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Delete a setting permanently. Admin access required.",
        operation_summary="Delete Setting",
        operation_id="delete_setting",
        tags=["System Management"],
        responses={
            200: openapi.Response(
                description="Setting deleted successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Setting deleted successfully"
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Authentication credentials were not provided"
                    }
                }
            ),
            403: openapi.Response(
                description="Admin access required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "You do not have permission to perform this action"
                    }
                }
            ),
            404: openapi.Response(
                description="Setting not found",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Setting not found"
                    }
                }
            )
        }
    )
    @handle_api_errors
    @log_api_call
    def delete(self, request, *args, **kwargs):
        """Delete setting (admin only)"""
        try:
            setting = self.get_object()
            setting_code = setting.setting_code
            setting.delete()
            
            return Response({
                'success': True,
                'message': f'Setting "{setting_code}" deleted successfully'
            })
        except Exception as e:
            logger.error(f"Error deleting setting: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to delete setting'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SettingsByCodeView(APIView):
    """
    Get setting by code endpoint.
    
    GET: Get setting value by setting_code (any authenticated user)
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get a setting value by its unique setting_code. Accessible to any authenticated user.",
        operation_summary="Get Setting by Code",
        operation_id="get_setting_by_code",
        tags=["System Management"],
        manual_parameters=[
            openapi.Parameter(
                'setting_code',
                openapi.IN_PATH,
                description="Unique identifier for the setting (e.g., 'theme_config', 'api_limits')",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Setting retrieved successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "setting_code": "theme_config",
                            "setting_value": {"primary_color": "#007bff", "dark_mode": True},
                            "description": "Frontend theme configuration",
                            "is_active": True,
                            "created_at": "2025-01-27T12:00:00Z",
                            "updated_at": "2025-01-27T12:00:00Z"
                        }
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Authentication credentials were not provided"
                    }
                }
            ),
            404: openapi.Response(
                description="Setting not found",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Setting not found"
                    }
                }
            )
        }
    )
    @handle_api_errors
    @log_api_call
    def get(self, request, setting_code):
        """Get setting by code"""
        try:
            setting = Settings.objects.get(setting_code=setting_code, is_active=True)
            serializer = SettingsSerializer(setting)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Settings.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Setting not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving setting by code: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to retrieve setting'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
