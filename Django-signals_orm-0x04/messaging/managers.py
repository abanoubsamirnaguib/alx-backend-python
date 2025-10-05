from django.db import models


class MessageQuerySet(models.QuerySet):
    def with_participants(self):
        return self.select_related('sender', 'receiver', 'parent_message', 'edited_by')

    def roots(self):
        return self.filter(parent_message__isnull=True)

    def with_immediate_replies(self):
        from .models import Message  # local import to avoid circular
        return self.with_participants().prefetch_related(
            models.Prefetch(
                'replies',
                queryset=Message.objects.with_participants().order_by('created_at')
            )
        )

    # kept for completeness, not strictly needed for the required API name
    def unread_for(self, user):
        return self.filter(receiver=user, read=False)


class UnreadMessagesManager(models.Manager):
    """Manager that returns only unread messages.

    Required API: Message.unread.unread_for_user(user)
    """
    def get_queryset(self):
        return super().get_queryset().filter(read=False)

    def unread_for_user(self, user):
        return self.get_queryset().filter(receiver=user)
