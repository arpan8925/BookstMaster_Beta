from django.db import models
from django.conf import settings
from authentication.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid

# Create your models here.
class Ticket(models.Model):

    STATUS_CHOICES = [

        ('pending', 'Pending'),

        ('in_progress', 'In Progress'),

        ('completed', 'Completed'),

        ('closed', 'Closed'),

    ]

    PRIORITY_CHOICES = [

        ('low', 'Low'),

        ('medium', 'Medium'),

        ('high', 'High'),

    ]



    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')

    subject = models.CharField(max_length=200)

    description = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    created = models.DateTimeField(auto_now_add=True)

    changed = models.DateTimeField(auto_now=True)

    unread = models.BooleanField(default=True)

    uid = models.IntegerField(null=True, blank=True)

    ids = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:

        ordering = ['-created']

        db_table = 'tickets'



    def __str__(self):

        return f"#{self.id} - {self.subject}"

    def delete_if_old(self):
        """Delete ticket if it's closed and older than 3 days"""
        if self.status == 'closed':
            cutoff_date = timezone.now() - timedelta(days=3)
            if self.changed <= cutoff_date:
                self.delete()
                return True
        return False

    @property
    def scheduled_deletion(self):
        """Return scheduled deletion date if ticket is closed"""
        if self.status == 'closed':
            from django.core.cache import cache
            cache_key = f'ticket_deletion_{self.id}'
            return cache.get(cache_key)
        return None

@receiver(post_save, sender=Ticket)
def check_old_tickets(sender, instance, **kwargs):
    """Check and delete old closed tickets when any ticket is saved"""
    if instance.status == 'closed':
        # Schedule deletion after 3 days
        from django.core.cache import cache
        from django.db import transaction
        
        # Set a cache key for this ticket's scheduled deletion
        cache_key = f'ticket_deletion_{instance.id}'
        
        # Only set if not already scheduled
        if not cache.get(cache_key):
            # Schedule deletion
            deletion_date = timezone.now() + timedelta(days=3)
            cache.set(cache_key, deletion_date, timeout=3*24*60*60)  # 3 days in seconds



class TicketMessage(models.Model):

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField()

    created = models.DateTimeField(auto_now_add=True)

    changed = models.DateTimeField(auto_now=True)

    is_read = models.BooleanField(default=False)

    uid = models.IntegerField(null=True, blank=True)

    ids = models.CharField(max_length=255, null=True, blank=True)



    class Meta:

        ordering = ['created']

        db_table = 'ticket_messages'



    def __str__(self):

        return f"Message for Ticket #{self.ticket.id}"



class Transaction(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_transactions'
    )
    transaction_id = models.CharField(
        max_length=100, 
        unique=True, 
        null=True,  
        blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created']
        db_table = 'transactions'

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        if not self.total_amount:
            self.total_amount = self.amount + self.fee
        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_string = str(uuid.uuid4()).split('-')[0]
        return f"TXN-{timestamp}-{random_string}"

    def __str__(self):
        return f"{self.transaction_id} - {self.user.username} - ${self.amount}"



class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('refunded', 'Refunded')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey('managerdashboard.Service', on_delete=models.CASCADE)
    link = models.URLField()
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created']
        db_table = 'orders'

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


