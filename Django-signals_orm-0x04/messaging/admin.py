from django.contrib import admin

from .models import Message, Notification, MessageHistory


class MessageHistoryInline(admin.TabularInline):
    model = MessageHistory
    extra = 0
    readonly_fields = ("old_content", "edited_at", "edited_by")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "short_content", "created_at", "edited")
    list_filter = ("created_at", "sender", "receiver", "edited")
    search_fields = ("content", "sender__username", "receiver__username")
    inlines = [MessageHistoryInline]
    readonly_fields = ("edited", "edited_at")

    def short_content(self, obj):
        return (obj.content[:30] + '...') if len(obj.content) > 30 else obj.content


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message__content")