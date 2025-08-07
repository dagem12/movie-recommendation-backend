from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from utils.cache_service import cache_service
from .serializers import RegisterSerializer, FavoriteMovieSerializer, AddFavoriteMovieSerializer
from .models import FavoriteMovie

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer to include additional user info"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add custom claims
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data

class LoginView(TokenObtainPairView):
    """Custom login view with additional user information"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

class RefreshTokenView(TokenRefreshView):
    """Refresh token view"""
    permission_classes = [AllowAny]

class UserInfoView(generics.RetrieveAPIView):
    """
    Get user information with caching
    
    Features:
    - Returns user profile information
    - Caches user data for 15 minutes
    - Invalidates cache when user data changes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Try to get from cache first
        cached_user_info = cache_service.get_user_info(user.id)
        if cached_user_info:
            return Response({
                'success': True,
                'data': cached_user_info,
                'cached': True
            })
        
        # If not in cache, build user info
        user_info = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'favorites_count': FavoriteMovie.objects.filter(user=user).count()
        }
        
        # Cache the user info
        cache_service.set_user_info(user.id, user_info)
        
        return Response({
            'success': True,
            'data': user_info,
            'cached': False
        })

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Invalidate any related caches if needed
        # Note: New user won't have cached data yet, but this is good practice
        if response.status_code == 201:
            user_id = response.data.get('id')
            if user_id:
                cache_service.invalidate_user_cache(user_id)
        
        return response

class FavoriteMovieListView(generics.ListAPIView):
    """
    View to list all favorite movies for the authenticated user.
    
    Returns a paginated list of movies the user has marked as favorites.
    """
    serializer_class = FavoriteMovieSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return favorite movies for the current user"""
        return FavoriteMovie.objects.filter(user=self.request.user)

class AddFavoriteMovieView(generics.CreateAPIView):
    """
    View to add a movie to user's favorites.
    
    Accepts movie data and creates a new favorite entry for the authenticated user.
    """
    serializer_class = AddFavoriteMovieSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Override create to handle duplicate favorites gracefully"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if movie is already in favorites
        user = request.user
        tmdb_id = serializer.validated_data['tmdb_id']
        
        if FavoriteMovie.objects.filter(user=user, tmdb_id=tmdb_id).exists():
            return Response(
                {'detail': 'Movie is already in your favorites'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        favorite = serializer.save()
        
        # Invalidate user cache since favorites count changed
        cache_service.invalidate_user_cache(request.user.id)
        
        return Response(
            FavoriteMovieSerializer(favorite).data,
            status=status.HTTP_201_CREATED
        )

class RemoveFavoriteMovieView(generics.DestroyAPIView):
    """
    View to remove a movie from user's favorites.
    
    Deletes the favorite movie entry for the authenticated user.
    """
    serializer_class = FavoriteMovieSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only favorite movies belonging to the current user"""
        return FavoriteMovie.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to provide custom response"""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        # Invalidate user cache since favorites count changed
        cache_service.invalidate_user_cache(request.user.id)
        
        return Response(
            {'detail': 'Movie removed from favorites successfully'},
            status=status.HTTP_200_OK
        )

class CheckFavoriteMovieView(generics.RetrieveAPIView):
    """
    View to check if a movie is in user's favorites.
    
    Returns whether a specific movie (by TMDB ID) is in the user's favorites.
    """
    serializer_class = FavoriteMovieSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get favorite movie by TMDB ID for current user"""
        tmdb_id = self.kwargs.get('tmdb_id')
        try:
            return FavoriteMovie.objects.get(user=self.request.user, tmdb_id=tmdb_id)
        except FavoriteMovie.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to handle non-existent favorites"""
        instance = self.get_object()
        if instance is None:
            return Response(
                {'is_favorite': False, 'detail': 'Movie not in favorites'},
                status=status.HTTP_200_OK
            )
        
        serializer = self.get_serializer(instance)
        return Response({
            'is_favorite': True,
            'favorite_data': serializer.data
        })