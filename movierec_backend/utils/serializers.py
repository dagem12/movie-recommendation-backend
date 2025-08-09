from rest_framework import serializers
from .models import Settings
import json

class SettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the Settings model.
    
    Provides validation and serialization for setting configurations.
    """
    
    class Meta:
        model = Settings
        fields = ['id', 'setting_code', 'setting_value', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_setting_code(self, value):
        """
        Validate setting code format and uniqueness.
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Setting code cannot be empty")
        
        # Check for valid characters (alphanumeric, underscore, hyphen)
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Setting code can only contain alphanumeric characters, underscores, and hyphens")
        
        return value.strip()

    def validate_setting_value(self, value):
        """
        Validate that the setting value is valid JSON-serializable data.
        """
        if value is None:
            raise serializers.ValidationError("Setting value cannot be null")
        
        try:
            # Test JSON serialization
            json.dumps(value)
        except (TypeError, ValueError) as e:
            raise serializers.ValidationError(f"Setting value must be valid JSON data: {str(e)}")
        
        return value

    def validate(self, data):
        """
        Additional validation for the entire object.
        """
        # Ensure setting code is not too long when combined with other data
        if 'setting_code' in data and len(data['setting_code']) > 100:
            raise serializers.ValidationError("Setting code is too long")
        
        return data

class SettingsListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing settings (without sensitive details).
    """
    
    class Meta:
        model = Settings
        fields = ['id', 'setting_code', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SettingsCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new settings.
    """
    
    class Meta:
        model = Settings
        fields = ['setting_code', 'setting_value', 'description', 'is_active']

    def validate_setting_code(self, value):
        """
        Validate setting code format and check for duplicates.
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Setting code cannot be empty")
        
        # Check for valid characters
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Setting code can only contain alphanumeric characters, underscores, and hyphens")
        
        # Check if setting code already exists
        if Settings.objects.filter(setting_code=value.strip()).exists():
            raise serializers.ValidationError("Setting code already exists")
        
        return value.strip()

class SettingsUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing settings.
    """
    
    class Meta:
        model = Settings
        fields = ['setting_value', 'description', 'is_active']
        read_only_fields = ['setting_code']  # Cannot change setting code after creation
