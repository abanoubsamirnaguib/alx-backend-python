from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from django.utils import timezone

from .models import Message, Notification, MessageHistory


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    # When a new message is created, make a notification for the receiver
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_save, sender=Message)
def store_previous_version(sender, instance, **kwargs):
    """Before saving an existing Message, store its old content if changed.

    We mark the message as edited and set edited_at/edited_by if not already set.
    (edited_by can be set by caller before save; we don't overwrite if present.)
    """
    if not instance.pk:  # new message, nothing to version
        return
    try:
        old = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return
    # Only act if content actually changed
    if old.content != instance.content:
        MessageHistory.objects.create(
            message=old,
            old_content=old.content,
            edited_by=instance.edited_by  # may be None
        )
        instance.edited = True
        if instance.edited_at is None:
            instance.edited_at = timezone.now()