from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
from user_dashboard.models import Ticket

class Command(BaseCommand):
    help = 'Checks and deletes tickets scheduled for deletion'

    def handle(self, *args, **options):
        # Get all closed tickets
        closed_tickets = Ticket.objects.filter(status='closed')
        deleted_count = 0
        
        for ticket in closed_tickets:
            cache_key = f'ticket_deletion_{ticket.id}'
            deletion_date = cache.get(cache_key)
            
            if deletion_date and timezone.now() >= deletion_date:
                ticket.delete()
                cache.delete(cache_key)
                deleted_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} scheduled tickets')
        ) 