from django.urls import path
from .views import delete_user, create_message, inbox_threads, thread_detail, unread_inbox

urlpatterns = [
    path('delete-account/', delete_user, name='delete_user'),
    path('messages/create/', create_message, name='create_message'),
    path('messages/inbox/', inbox_threads, name='inbox_threads'),
    path('messages/inbox/unread/', unread_inbox, name='unread_inbox'),
    path('messages/thread/<int:message_id>/', thread_detail, name='thread_detail'),
]
