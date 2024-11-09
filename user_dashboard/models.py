from django.db import models
from django.conf import settings
from authentication.models import User



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

    content = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    unread = models.BooleanField(default=True)



    class Meta:

        ordering = ['-created_at']



    def __str__(self):

        return f"{self.subject} - {self.user.email}"



class TicketReply(models.Model):

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_staff_reply = models.BooleanField(default=False)



    class Meta:

        ordering = ['created_at']


