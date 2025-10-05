from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Message, Notification, MessageHistory

User = get_user_model()


class MessageSignalTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='pass1234')
        self.bob = User.objects.create_user(username='bob', password='pass1234')

    def test_notification_created_on_message(self):
        self.assertEqual(Notification.objects.count(), 0)
        msg = Message.objects.create(sender=self.alice, receiver=self.bob, content='Hello Bob!')
        self.assertEqual(Notification.objects.count(), 1)
        note = Notification.objects.first()
        self.assertEqual(note.user, self.bob)
        self.assertEqual(note.message, msg)
        self.assertFalse(note.is_read)

    def test_no_extra_notification_on_update(self):
        msg = Message.objects.create(sender=self.alice, receiver=self.bob, content='Hello Bob!')
        self.assertEqual(Notification.objects.count(), 1)
        # update message content
        msg.content = 'Hello Bob!!'
        msg.save()
        # still only one notification
        self.assertEqual(Notification.objects.count(), 1)

    def test_multiple_messages_create_multiple_notifications(self):
        for i in range(3):
            Message.objects.create(sender=self.alice, receiver=self.bob, content=f'Message {i}')
        self.assertEqual(Notification.objects.count(), 3)
        users = {n.user for n in Notification.objects.all()}
        self.assertEqual(users, {self.bob})

    def test_edit_creates_history_entry(self):
        msg = Message.objects.create(sender=self.alice, receiver=self.bob, content='Original')
        self.assertEqual(MessageHistory.objects.count(), 0)
        msg.content = 'Changed'
        msg.edited_by = self.alice
        msg.save()
        self.assertEqual(MessageHistory.objects.count(), 1)
        hist = MessageHistory.objects.first()
        self.assertEqual(hist.old_content, 'Original')
        self.assertEqual(hist.edited_by, self.alice)
        # message marked edited
        msg.refresh_from_db()
        self.assertTrue(msg.edited)
        self.assertIsNotNone(msg.edited_at)

    def test_edit_without_content_change_no_history(self):
        msg = Message.objects.create(sender=self.alice, receiver=self.bob, content='Hello')
        msg.edited_by = self.alice
        msg.save()  # no change to content
        self.assertEqual(MessageHistory.objects.count(), 0)

    def test_multiple_edits_create_multiple_history_rows(self):
        msg = Message.objects.create(sender=self.alice, receiver=self.bob, content='v1')
        for content in ['v2', 'v3', 'v4']:
            msg.content = content
            msg.edited_by = self.alice
            msg.save()
        self.assertEqual(MessageHistory.objects.count(), 3)
        # newest history corresponds to previous version 'v3'
        newest = MessageHistory.objects.order_by('-edited_at').first()
        self.assertEqual(newest.old_content, 'v3')