from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import secrets
import uuid

class User(AbstractUser):
    # Fields from the general_users table
    ids = models.CharField(max_length=32, unique=True, blank=True, null=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) #Unique ID for the user
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('user', 'User')], default='user')
    login_type = models.TextField(blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=75, blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    timezone = models.TextField(blank=True, null=True) 
    more_information = models.JSONField(blank=True, null=True)
    settings = models.TextField(blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    balance = models.DecimalField(max_digits=5, decimal_places=3, default=0.000)
    custom_rate = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    api_key = models.CharField(max_length=191, unique=True, blank=True, null=True)
    spent = models.DecimalField(max_digits=15, decimal_places=4, null=True)
    activation_key = models.CharField(max_length=191, blank=True, null=True)
    reset_key = models.CharField(max_length=191, blank=True, null=True)
    history_ip = models.CharField(max_length=17, blank=True, null=True)
    status = models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')])
    level = models.CharField(
    max_length=15, 
    choices=[
        ('silver-member', 'Silver Member'),
        ('gold-elite', 'Gold Elite'),
        ('platinum-status', 'Platinum Status'),
        ('diamond-master', 'Diamond Master'),
        ('ultimate-legend', 'Ultimate Legend')
    ], 
    default='silver-member'
    )
    changed = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generate the 'ids' field if it's not set already
        if not self.ids:
            self.ids = str(uuid.uuid4()).replace('-', '')

        # Auto-generate API key if it doesn't exist
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(32)

        if not self.uid:
            self.uid = uuid.uuid4()

        # Ensure uniqueness of the API key
        while User.objects.filter(api_key=self.api_key).exists():
            self.api_key = secrets.token_urlsafe(32)

        # Auto-generate activation key if it doesn't exist
        if not self.activation_key:
            self.activation_key = secrets.token_urlsafe(32)

        # Ensure uniqueness of the activation key
        while User.objects.filter(activation_key=self.activation_key).exists():
            self.activation_key = secrets.token_urlsafe(32)

        # Auto-generate reset key if it doesn't exist
        if not self.reset_key:
            self.reset_key = secrets.token_urlsafe(32)

        # Ensure uniqueness of the reset key
        while User.objects.filter(reset_key=self.reset_key).exists():
            self.reset_key = secrets.token_urlsafe(32)

        super().save(*args, **kwargs)


    def generate_api_key(self):
        """Generate a new unique API key"""
        new_key = secrets.token_urlsafe(32)
        # Ensure uniqueness of the API key
        while User.objects.filter(api_key=new_key).exists():
            new_key = secrets.token_urlsafe(32)  # Regenerate if the generated key already exists
        self.api_key = new_key
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