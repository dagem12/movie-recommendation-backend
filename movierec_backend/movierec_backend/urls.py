"""
URL configuration for movierec_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Health check view
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'movie-recommendation-backend',
        'timestamp': '2025-01-27T12:00:00Z'
    })

# Swagger Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="Movie Recommendation API",
        default_version='v1',
        description="A comprehensive API for movie recommendations, user management, and movie data retrieval.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@movierec.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
    
    # Health check endpoint for Docker
    path('health/', health_check, name='health_check'),
    
    # API Documentation URLs
    re_path(r'^api/docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints
    path('api/users/', include('users.urls')),
    path('api/movies/', include('movies.urls')),
    path('api/utils/', include('utils.urls')),
]
