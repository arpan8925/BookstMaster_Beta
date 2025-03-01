from django.contrib import admin
from .models import Ticket, TicketMessage
from managerdashboard.models import Transactions

admin.site.register(Ticket)
admin.site.register(TicketMessage)
