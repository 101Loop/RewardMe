from django.dispatch import receiver
from simple_history.signals import pre_create_historical_record

from transactions.models import RewardPoints


@receiver(pre_create_historical_record)
def pre_create_historical_record_callback(sender, **kwargs):
    instance = kwargs["instance"]
    history_instance = kwargs["history_instance"]
    if isinstance(instance, RewardPoints):
        instance.refresh_from_db()
        history_instance.points = instance.points
