from django.db import models
from django.core.exceptions import ValidationError
import json

# Create your models here.

class Settings(models.Model):
    """
    Settings model for storing frontend system configuration values.
    
    This model allows storing various configuration settings as JSON values,
    making it flexible for different types of frontend configurations.
    """
    setting_code = models.CharField(
        max_length=100, 
        unique=True, 
        help_text="Unique identifier for the setting (e.g., 'theme_config', 'api_limits')"
    )
    setting_value = models.JSONField(
        help_text="JSON value for the setting configuration"
    )
    description = models.TextField(
        blank=True, 
        help_text="Optional description of what this setting controls"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether this setting is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"
        ordering = ['setting_code']
        db_table = 'utils_settings'

    def __str__(self):
        return f"{self.setting_code}: {str(self.setting_value)[:50]}..."

    def clean(self):
        """Validate JSON data"""
        if self.setting_value is not None:
            try:
                # Ensure the value can be serialized to JSON
                json.dumps(self.setting_value)
            except (TypeError, ValueError):
                raise ValidationError("setting_value must contain valid JSON data")

    def save(self, *args, **kwargs):
        """Validate before saving"""
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_setting(cls, setting_code, default=None):
        """
        Get a setting value by code.
        
        Args:
            setting_code (str): The setting code to retrieve
            default: Default value if setting doesn't exist
            
        Returns:
            The setting value or default
        """
        try:
            setting = cls.objects.get(setting_code=setting_code, is_active=True)
            return setting.setting_value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_setting(cls, setting_code, setting_value, description="", is_active=True):
        """
        Set or update a setting value.
        
        Args:
            setting_code (str): The setting code
            setting_value: The JSON value to store
            description (str): Optional description
            is_active (bool): Whether the setting is active
            
        Returns:
            The Settings instance
        """
        setting, created = cls.objects.update_or_create(
            setting_code=setting_code,
            defaults={
                'setting_value': setting_value,
                'description': description,
                'is_active': is_active
            }
        )
        return setting
