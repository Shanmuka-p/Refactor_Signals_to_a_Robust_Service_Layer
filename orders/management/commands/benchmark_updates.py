import time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import F
from orders.models import Order, UserStats


class Command(BaseCommand):
    help = 'Benchmarks signal-like sequential creation vs. optimized bulk service layer operations.'

    def handle(self, *args, **options):
        # Setup benchmark test users
        user_signal, _ = User.objects.get_or_create(username='benchmark_signal')
        user_service, _ = User.objects.get_or_create(username='benchmark_service')

        # Clean existing test data for accurate measurement
        UserStats.objects.filter(user__in=[user_signal, user_service]).delete()
        Order.objects.filter(user__in=[user_signal, user_service]).delete()

        num_orders = 1000
        order_total = Decimal('10.00')

        # ----------------------------------------------------
        # 1. Signal Simulation (N+1 Query Loop)
        # ----------------------------------------------------
        start_signal = time.perf_counter()
        stats_signal, _ = UserStats.objects.get_or_create(user=user_signal)
        for _ in range(num_orders):
            Order.objects.create(user=user_signal, total=order_total)
            stats_signal.order_count += 1
            stats_signal.total_spent += order_total
            stats_signal.save()
        signal_time = time.perf_counter() - start_signal

        # ----------------------------------------------------
        # 2. Optimized Service Layer Approach (Bulk Insert + Single Update)
        # ----------------------------------------------------
        start_service = time.perf_counter()
        orders_to_create = [
            Order(user=user_service, total=order_total)
            for _ in range(num_orders)
        ]
        Order.objects.bulk_create(orders_to_create)

        UserStats.objects.get_or_create(user=user_service)

        total_addition = order_total * num_orders
        UserStats.objects.filter(user=user_service).update(
            order_count=F('order_count') + num_orders,
            total_spent=F('total_spent') + total_addition
        )
        service_time = time.perf_counter() - start_service

        speedup = signal_time / service_time if service_time > 0 else 0.0

        # Exact output format mandated by contract specifications
        self.stdout.write(f"Signal approach time: {signal_time:.4f}s")
        self.stdout.write(f"Optimized service time: {service_time:.4f}s")
        self.stdout.write(f"Speedup factor: {speedup:.2f}x")
