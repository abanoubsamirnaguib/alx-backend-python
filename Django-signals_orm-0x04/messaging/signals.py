from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from django.utils import timezone

from django.contrib.auth import get_user_model

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


# --- User cleanup signals ---
User = get_user_model()


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """Extra cleanup after a user is deleted.

    Thanks to on_delete=CASCADE most related rows (messages, notifications, histories
    linked via messages) are already removed automatically by the database.

    We still explicitly remove MessageHistory rows where the user only appears as
    'edited_by' (that FK uses SET_NULL so they would otherwise remain). The
    requirement says: delete all message histories associated with the user.
    """
    # Delete histories where user was the editor (not covered by CASCADE)
    MessageHistory.objects.filter(edited_by=instance).delete()