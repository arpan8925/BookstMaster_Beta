from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from user_dashboard.models import Order

class OrderManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@test.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.admin_user,
            status='pending'
            # Add other required fields based on your Order model
        )

    def test_complete_order(self):
        # Login as admin
        self.client.login(email='admin@test.com', password='testpass123')
        
        # Make the complete order request
        response = self.client.post(
            reverse('complete_order', kwargs={'order_id': self.order.id})
        )
        
        # Check if request was successful
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Refresh order from database
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')
