from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class MessageQuerySet(models.QuerySet):
    """Extra helpers for optimizing message + replies fetching."""

    def with_participants(self):
        # pull in FK users and potential parent/edited_by in one go
        return self.select_related(
            'sender', 'receiver', 'parent_message', 'edited_by'
        )

    def roots(self):
        return self.filter(parent_message__isnull=True)

    def with_immediate_replies(self):
        # prefetch only first level replies (each with sender/receiver)
        return self.with_participants().prefetch_related(
            models.Prefetch(
                'replies',
                queryset=Message.objects.with_participants().order_by('created_at')
            )
        )


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    # NEW: parent message (for threaded replies)
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text='If set, this message is a reply to parent_message.'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # edit tracking
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_messages'
    )

    objects = MessageQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

    # --- Thread helpers (simple + junior friendly) ---
    @property
    def is_root(self):
        return self.parent_message_id is None

    def get_all_replies(self):
        """Return a flat list of ALL descendant replies (any depth).

        Uses iterative breadth-first querying to keep memory simple.
        (Each level = 1 query; fine for modest thread depth.)
        """
        descendants = []
        current_ids = [self.id]
        # we always select related users for display efficiency
        while current_ids:
            children = list(
                Message.objects.filter(parent_message_id__in=current_ids)
                .select_related('sender', 'receiver', 'parent_message')
                .order_by('created_at')
            )
            if not children:
                break
            descendants.extend(children)
            current_ids = [m.id for m in children]
        return descendants

    def get_thread_messages(self):
        """Return [root_message] + all its descendants (flat list).

        If self is not the root we climb up first. List is ordered by
        created_at ascending inside each depth when later rendered.
        """
        root = self
        seen = set()
        # climb to root (depth usually tiny)
        while root.parent_message_id and root.parent_message_id not in seen:
            seen.add(root.id)
            root = root.parent_message  # already in memory due to select_related if caller used it
        return [root] + root.get_all_replies()

    def build_thread_tree(self):
        """Return a nested dict representing the thread for easy JSON/DRF use.

        We first fetch every descendant in a handful of queries (by depth),
        then build an in-memory tree so rendering is O(n).
        """
        root = self.get_thread_messages()[0]
        all_msgs = root.get_thread_messages()  # root + descendants
        # Map parent_id -> list of children
        children_map = {}
        for m in all_msgs[1:]:  # skip root which is first
            children_map.setdefault(m.parent_message_id, []).append(m)
        # sort each child group by created_at ascending (natural convo flow)
        for group in children_map.values():
            group.sort(key=lambda x: x.created_at)

        def serialize(msg):
            return {
                'id': msg.id,
                'content': msg.content,
                'sender': getattr(msg.sender, 'username', msg.sender_id),
                'receiver': getattr(msg.receiver, 'username', msg.receiver_id),
                'created_at': timezone.localtime(msg.created_at).isoformat() if msg.created_at else None,
                'edited': msg.edited,
                'replies': [serialize(child) for child in children_map.get(msg.id, [])]
            }

        return serialize(root)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user} about message {self.message_id}"


class MessageHistory(models.Model):
    """Stores previous versions of a message before edits.

    We only store the old content. The current (latest) content lives on Message.
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='message_histories'
    )

    class Meta:
        ordering = ['-edited_at']

    def __str__(self):
        return f"History of message {self.message_id} at {self.edited_at:%Y-%m-%d %H:%M:%S}" 