from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models


@receiver(post_save, sender=models.User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a Profile when a User is created.
    This ensures every user has a corresponding profile automatically.
    """
    if created:
        models.Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=models.User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the user's profile.
    """
    if hasattr(instance, 'user_profile'):
        instance.user_profile.save()
