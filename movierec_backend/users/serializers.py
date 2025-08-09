from django.contrib.auth.models import User
from rest_framework import serializers
from .models import FavoriteMovie

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user

class FavoriteMovieSerializer(serializers.ModelSerializer):
    """
    Serializer for FavoriteMovie model.
    
    Handles creating, listing, and deleting favorite movies.
    """
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = FavoriteMovie
        fields = ['id', 'user', 'tmdb_id', 'title', 'poster_path', 'overview', 'release_date', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        """Override create to automatically set the current user"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AddFavoriteMovieSerializer(serializers.Serializer):
    """
    Serializer for adding a movie to favorites.
    
    Accepts movie data from external API and creates a favorite entry.
    """
    tmdb_id = serializers.IntegerField(help_text="TMDB movie ID")
    title = serializers.CharField(max_length=255, help_text="Movie title")
    poster_path = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text="Movie poster path")
    overview = serializers.CharField(required=False, allow_blank=True, help_text="Movie overview/description")
    release_date = serializers.DateField(required=False, allow_null=True, help_text="Movie release date")
    
    def create(self, validated_data):
        """Create a new favorite movie for the current user"""
        user = self.context['request'].user
        favorite, created = FavoriteMovie.objects.get_or_create(
            user=user,
            tmdb_id=validated_data['tmdb_id'],
            defaults=validated_data
        )
        return favorite

class UserInfoSerializer(serializers.Serializer):
    """
    Serializer for user information response.
    
    Defines the schema for user profile data returned by UserInfoView.
    """
    id = serializers.IntegerField(help_text="User ID")
    username = serializers.CharField(help_text="Username")
    email = serializers.EmailField(help_text="User email address")
    date_joined = serializers.DateTimeField(help_text="Date when user joined")
    last_login = serializers.DateTimeField(allow_null=True, help_text="Last login timestamp")
    is_active = serializers.BooleanField(help_text="Whether user account is active")
    is_staff = serializers.BooleanField(help_text="Whether user has staff privileges")
    favorites_count = serializers.IntegerField(help_text="Number of favorite movies")