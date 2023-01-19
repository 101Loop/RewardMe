from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_reward_points(sender, instance, created, **kwargs):
    from transactions.models import RewardPoints

    if created:
        # TODO: do we want to give some initial points?
        RewardPoints.objects.create(user=instance)
