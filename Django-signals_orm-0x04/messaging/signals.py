from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Message, Notification


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    # When a new message is created, make a notification for the receiver
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)