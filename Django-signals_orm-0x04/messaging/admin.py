from django.contrib import admin

from .models import Message, Notification


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "short_content", "created_at")
    list_filter = ("created_at", "sender", "receiver")
    search_fields = ("content", "sender__username", "receiver__username")

    def short_content(self, obj):
        return (obj.content[:30] + '...') if len(obj.content) > 30 else obj.content


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message__content")