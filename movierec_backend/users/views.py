from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
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

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

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