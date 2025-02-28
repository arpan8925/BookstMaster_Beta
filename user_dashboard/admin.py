from django.contrib import admin
from .models import Order, Ticket, TicketMessage

# Register your models here.
admin.site.register(Order)
admin.site.register(Ticket)
admin.site.register(TicketMessage)
