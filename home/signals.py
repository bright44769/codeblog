from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from .mfa import send_mfa_code as issue_mfa_code
from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created: Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)


@receiver(user_logged_in)
def send_login_mfa_code(sender, request, user, **kwargs):
    issue_mfa_code(request, user)
