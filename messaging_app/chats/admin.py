from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""
    
    list_display = ('user_id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at', 'has_conversation')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('user_id', 'created_at', 'last_login', 'date_joined')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_id', 'phone_number', 'role', 'created_at')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role')
        }),
    )
    
    def has_conversation(self, obj):
        return hasattr(obj, 'conversation') and obj.conversation is not None
    has_conversation.boolean = True
    has_conversation.short_description = 'Has Conversation'


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin configuration for the Conversation model."""
    
    list_display = ('conversation_id', 'participants', 'get_message_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('conversation_id', 'participants__username', 'participants__email')
    readonly_fields = ('conversation_id', 'created_at', 'updated_at')
    ordering = ('-updated_at',)
    
    def get_message_count(self, obj):
        return obj.messages.count()
    get_message_count.short_description = 'Message Count'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for the Message model."""
    
    list_display = ('message_id', 'sender', 'conversation', 'get_message_preview', 'is_from_system', 'sent_at', 'is_deleted')
    list_filter = ('sent_at', 'is_deleted', 'edited_at', 'is_from_system')
    search_fields = ('sender__username', 'sender__email', 'message_body', 'conversation__conversation_id')
    readonly_fields = ('message_id', 'sent_at', 'edited_at')
    ordering = ('-sent_at',)
    
    def get_message_preview(self, obj):
        return obj.message_body[:50] + '...' if len(obj.message_body) > 50 else obj.message_body
    get_message_preview.short_description = 'Message Preview'
