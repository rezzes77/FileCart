from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """
    Создаем профиль, если пользователь создан.
    """
    try:
        if created:
            Profile.objects.create(user=instance)
        else:
            profile, _ = Profile.objects.get_or_create(user=instance)
            profile.save()
    except Exception as e:
        logger.error(f"Error managing profile for user {instance.id}: {e}")
