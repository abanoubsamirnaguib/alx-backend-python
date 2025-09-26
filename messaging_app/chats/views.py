from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action 

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsOwnerOfConversation, IsMessageOwnerOrConversationParticipant, CanCreateConversation
class ConversationViewSet(viewsets.ModelViewSet):
	"""List and create conversations. Each user can have only one conversation.

	list: list all conversations (admin or staff)
	create: create a conversation for a user (prevents duplicates)
	retrieve/update/destroy: operate on a single conversation
	"""
	queryset = Conversation.objects.all().select_related('participants')
	serializer_class = ConversationSerializer
	permission_classes = [permissions.IsAuthenticated, IsOwnerOfConversation, CanCreateConversation]
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = ['participants__username', 'participants__email']
	ordering_fields = ['created_at', 'updated_at']

	def get_queryset(self):
		user = self.request.user
		# Regular users only see their own conversation; staff can see all
		if user.is_staff or user.is_superuser:
			return self.queryset.prefetch_related('messages')
		return self.queryset.filter(participants=user).prefetch_related('messages')

	def create(self, request, *args, **kwargs):
		# Allow creating a conversation for the authenticated user by default
		data = request.data.copy()
		if 'participants_id' not in data and not (request.user.is_anonymous):
			data['participants_id'] = request.user.pk

		serializer = self.get_serializer(data=data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MessageViewSet(viewsets.ModelViewSet):
	"""List and create messages for conversations.

	list: list messages (scoped to conversation or user's conversation)
	create: send a message to an existing conversation
	"""
	queryset = Message.objects.all().select_related('sender', 'conversation')
	serializer_class = MessageSerializer
	permission_classes = [permissions.IsAuthenticated, IsMessageOwnerOrConversationParticipant]
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = ['message_body', 'sender__username', 'sender__email']
	ordering_fields = ['sent_at']

	def get_queryset(self):
		qs = self.queryset
		user = self.request.user
		conversation_id = self.request.query_params.get('conversation')
		if conversation_id:
			qs = qs.filter(conversation__conversation_id=conversation_id)
		elif not (user.is_staff or user.is_superuser):
			# default: user's own conversation messages
			qs = qs.filter(conversation__participants=user)
		return qs.order_by('-sent_at')

	def create(self, request, *args, **kwargs):
		data = request.data.copy()
		# If sender_id is not provided, use request.user
		if 'sender_id' not in data:
			data['sender_id'] = request.user.pk

		# Ensure conversation exists
		conversation = None
		if 'conversation' in data:
			# leave as-is, serializer will validate
			pass
		else:
			# try to find the user's conversation
			try:
				conversation = Conversation.objects.get(participants=request.user)
				data['conversation'] = conversation.conversation_id
			except Conversation.DoesNotExist:
				return Response({'conversation': 'Conversation not found for user.'}, status=status.HTTP_400_BAD_REQUEST)

		serializer = self.get_serializer(data=data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

