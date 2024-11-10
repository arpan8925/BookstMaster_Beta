from django.db import models

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[
        ('automatic', 'Automatic'),
        ('manual', 'Manual')
    ])
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('both', 'Both')
    ])
    fee_amount = models.DecimalField(max_digits=5, decimal_places=2)
    fee_fixed = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    client_id = models.CharField(max_length=255, blank=True, null=True)
    client_secret = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    test_mode = models.BooleanField(default=False)
    icon = models.ImageField(upload_to='payment_icons/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 