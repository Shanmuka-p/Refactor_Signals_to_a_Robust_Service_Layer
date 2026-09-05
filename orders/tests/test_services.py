from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from orders.models import Order, UserStats
from orders.services import create_order


class ServiceLayerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='service_user', password='password123')

    def test_create_order_service(self):
        """
        Verify that the service function create_order creates an Order and updates UserStats correctly.
        """
        order = create_order(self.user, Decimal('150.75'))

        # Assert Order object is created
        self.assertIsNotNone(order.id)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total, Decimal('150.75'))

        # Assert corresponding UserStats object is created/updated correctly
        stats = UserStats.objects.get(user=self.user)
        self.assertEqual(stats.order_count, 1)
        self.assertEqual(stats.total_spent, Decimal('150.75'))

        # Call service again
        order2 = create_order(self.user, Decimal('49.25'))
        stats.refresh_from_db()
        self.assertEqual(stats.order_count, 2)
        self.assertEqual(stats.total_spent, Decimal('200.00'))

    def test_direct_order_create_does_not_trigger_stats_update(self):
        """
        Verify that creating an order directly via Order.objects.create() does NOT update UserStats,
        proving that signal handling has been removed from global execution.
        """
        Order.objects.create(user=self.user, total=Decimal('100.00'))

        # UserStats should NOT be created or updated automatically
        stats_exists = UserStats.objects.filter(user=self.user).exists()
        self.assertFalse(stats_exists)
