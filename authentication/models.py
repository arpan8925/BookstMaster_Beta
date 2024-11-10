from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import secrets

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    timezone = models.CharField(max_length=50, default='UTC')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    skype = models.CharField(max_length=50, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    api_key = models.CharField(max_length=64, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = self.generate_api_key()
        super().save(*args, **kwargs)

    def generate_api_key(self):
        """Generate a new API key"""
        new_key = secrets.token_urlsafe(32)
        self.api_key = new_key
        self.save(update_fields=['api_key'])
        return new_key

    def __str__(self):
        return self.username

@receiver(post_migrate)
def create_manager_permission(sender, **kwargs):
    # Only run this when migrating the authentication app
    if sender.name != 'authentication':
        return
        
    # Get the content type for our custom User model
    content_type = ContentType.objects.get_for_model(User)
    
    # Create the permission if it doesn't exist
    Permission.objects.get_or_create(
        codename='is_manager',
        name='Is Manager User',
        content_type=content_type,
    )