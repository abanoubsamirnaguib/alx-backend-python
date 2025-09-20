import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Includes additional fields as per the database specification.
    """
    
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    
    # Use UUID as primary key
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Override first_name and last_name to make them required
    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    
    # Email field (already unique in AbstractUser, but ensuring it's required)
    email = models.EmailField(unique=True, null=False, blank=False, db_index=True)
    
    # Additional fields
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='guest',
        null=False,
        blank=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Override username requirement from AbstractUser
    username = models.CharField(
        max_length=150,
        unique=True,
        null=False,
        blank=False
    )

    password = models.CharField(max_length=128, null=False, blank=False)
    
    class Meta:
        db_table = 'chats_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    """
    Model representing a conversation for a single user with the system.
    Each user has exactly one conversation.
    """
    
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    participants = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='conversation',
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chats_conversation'
        indexes = [
            models.Index(fields=['conversation_id']),
            models.Index(fields=['participants']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation for {self.participants.username}"


class Message(models.Model):
    """
    Model representing a message in a user's conversation with the system.
    Links to sender (User) and the user's conversation.
    """
    
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        db_index=True
    )
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        db_index=True
    )
    
    message_body = models.TextField(null=False, blank=False)
    
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    # Flag to distinguish between user and system messages
    is_from_system = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'chats_message'
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
            models.Index(fields=['sent_at']),
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['is_from_system']),
        ]
        ordering = ['-sent_at']
    
    def __str__(self):
        message_type = "System" if self.is_from_system else "User"
        return f"{message_type} message from {self.sender} at {self.sent_at}"
