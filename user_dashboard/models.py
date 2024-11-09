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


