from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().select_related('participants')
    serializer_class = ConversationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__username', 'participants__email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        return self.queryset.filter(participants=user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user = request.user
        if 'participants_id' not in data and not user.is_anonymous:
            data['participants_id'] = user.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related('sender', 'conversation')
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body', 'sender__username', 'sender__email']
    ordering_fields = ['sent_at', 'edited_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        return Message.objects.filter(conversation__participants=user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user = request.user
        if 'sender_id' not in data:
            data['sender_id'] = user.pk
        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
