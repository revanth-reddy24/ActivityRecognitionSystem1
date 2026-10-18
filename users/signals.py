from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when a new user is created"""
    if created:
        # use get_or_create to be idempotent in case something else also created a profile
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    # profile may not exist in rare cases; guard against DoesNotExist
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # If profile does not exist, create it so subsequent saves won't fail
        UserProfile.objects.create(user=instance)