from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, UserStats


@receiver(post_save, sender=Order)
def update_user_stats_on_order_save(sender, instance, created, **kwargs):
    """
    Update UserStats whenever an Order is saved.
    Used for signal demonstration and test isolation cases.
    """
    if created:
        user = instance.user
        stats, _ = UserStats.objects.get_or_create(user=user)
        stats.order_count += 1
        stats.total_spent += instance.total
        stats.save()


# Disconnect signal by default for refactored Service Layer architecture
post_save.disconnect(receiver=update_user_stats_on_order_save, sender=Order)
