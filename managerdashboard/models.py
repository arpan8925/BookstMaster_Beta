from django.db import models
from authentication.models import User
from decimal import Decimal

# Create your models here.

class Provider(models.Model):
    name = models.CharField(max_length=200)
    api_url = models.URLField()
    api_key = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class ProviderTransaction(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    notes = models.TextField(blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} - ${self.amount} - {self.provider.name}"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('waiting', 'Waiting'),
        ('cancelled', 'Cancelled')
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='manager_transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transactions_added')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} - ${self.amount} - {self.user.username}"

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Service Categories'

    def __str__(self):
        return self.name

class Service(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]

    service_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='services', null=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name='services')
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    min_order = models.IntegerField()
    max_order = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_drip_feed = models.BooleanField(default=False)
    drip_feed_rules = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

class ServiceUpdate(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='updates')
    old_rate = models.DecimalField(max_digits=10, decimal_places=4)
    new_rate = models.DecimalField(max_digits=10, decimal_places=4)
    old_min = models.IntegerField()
    new_min = models.IntegerField()
    old_max = models.IntegerField()
    new_max = models.IntegerField()
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Update for {self.service.name} at {self.created_at}"

class PaymentMethod(models.Model):
    TYPE_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic')
    ]
    FEE_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('both', 'Both')
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    client_id = models.CharField(max_length=255, blank=True, null=True)
    client_secret = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    test_mode = models.BooleanField(default=False)
    icon = models.ImageField(upload_to='payment_icons/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name