from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from user_dashboard.models import Ticket

class Command(BaseCommand):
    help = 'Deletes closed tickets that are older than 3 days'

    def handle(self, *args, **options):
        # Calculate the cutoff date (3 days ago)
        cutoff_date = timezone.now() - timedelta(days=3)
        
        # Get closed tickets older than 3 days
        old_tickets = Ticket.objects.filter(
            status='closed',
            changed__lte=cutoff_date
        )
        
        # Count tickets to be deleted
        count = old_tickets.count()
        
        # Delete the tickets and their related messages (cascade delete)
        old_tickets.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} closed tickets older than 3 days')
        ) 