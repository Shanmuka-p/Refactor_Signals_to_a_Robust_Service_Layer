from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from orders.models import Order, UserStats
from orders.signals import update_user_stats_on_order_save


class SignalBehaviorTests(TestCase):
    def setUp(self):
        # Connect signal receiver explicitly for testing signal behavior
        post_save.connect(update_user_stats_on_order_save, sender=Order)
        self.user1 = User.objects.create_user(username='signal_user1', password='password123')
        self.user2 = User.objects.create_user(username='signal_user2', password='password123')

    def tearDown(self):
        # Disconnect signal receiver after test runs to demonstrate test isolation
        post_save.disconnect(receiver=update_user_stats_on_order_save, sender=Order)

    def test_signal_updates_user_stats_on_order_create(self):
        """
        Verify that post_save signal updates UserStats when Order.objects.create() is called.
        """
        Order.objects.create(user=self.user1, total=Decimal('100.00'))
        stats = UserStats.objects.get(user=self.user1)
        self.assertEqual(stats.order_count, 1)
        self.assertEqual(stats.total_spent, Decimal('100.00'))

    def test_bulk_update_bypasses_signal(self):
        """
        Demonstrates and proves that QuerySet.update() bypasses the post_save signal.
        """
        # Step 1: Create a User and at least two Order instances for that user using Order.objects.create()
        order1 = Order.objects.create(user=self.user1, total=Decimal('50.00'))
        order2 = Order.objects.create(user=self.user1, total=Decimal('75.00'))

        # Step 2: Verify that initial UserStats are correct
        stats = UserStats.objects.get(user=self.user1)
        self.assertEqual(stats.order_count, 2)
        self.assertEqual(stats.total_spent, Decimal('125.00'))

        # Step 3: Create a new Order for the same user (updates stats)
        order3 = Order.objects.create(user=self.user1, total=Decimal('25.00'))
        stats.refresh_from_db()
        self.assertEqual(stats.order_count, 3)
        self.assertEqual(stats.total_spent, Decimal('150.00'))

        # Step 4: Create several more Order objects for a different user using bulk_create
        bulk_orders = Order.objects.bulk_create([
            Order(user=self.user2, total=Decimal('200.00')),
            Order(user=self.user2, total=Decimal('300.00')),
        ])

        # Step 5: Change the user of the bulk-created orders to the first user using QuerySet.update()
        Order.objects.filter(id__in=[o.id for o in bulk_orders]).update(user=self.user1)

        # Step 6: Fetch the UserStats for the first user again
        stats.refresh_from_db()

        # Step 7: Assert that the UserStats have not changed after the update() call
        self.assertEqual(stats.order_count, 3)
        self.assertEqual(stats.total_spent, Decimal('150.00'))
