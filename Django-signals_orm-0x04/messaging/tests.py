from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Message, Notification

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