from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action 
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import (
    IsParticipantOfConversation, 
    IsAuthenticatedAndParticipant, 
    CanManageOwnMessages,
    CanCreateConversation
)
from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination, ConversationPagination, CustomMessagePagination
class ConversationViewSet(viewsets.ModelViewSet):
	"""List and create conversations. Each user can have only one conversation.

	list: list all conversations (admin or staff)
	create: create a conversation for a user (prevents duplicates)
	retrieve/update/destroy: operate on a single conversation
	"""
	queryset = Conversation.objects.all().select_related('participants')
	serializer_class = ConversationSerializer
	permission_classes = [IsParticipantOfConversation, CanCreateConversation]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_class = ConversationFilter
	search_fields = ['participants__username', 'participants__email']
	ordering_fields = ['created_at', 'updated_at']
	ordering = ['-updated_at']
	pagination_class = ConversationPagination

	def get_queryset(self):
		user = self.request.user
		# Regular users only see their own conversation; staff can see all
		if user.is_staff or user.is_superuser:
			return self.queryset.prefetch_related('messages')
		return self.queryset.filter(participants=user).prefetch_related('messages')

	def create(self, request, *args, **kwargs):
		"""
		Create a conversation with proper access control
		"""
		# Allow creating a conversation for the authenticated user by default
		data = request.data.copy()
		user = request.user
		
		if 'participants_id' not in data and not user.is_anonymous:
			data['participants_id'] = user.pk
		else:
			# Check if user is trying to create a conversation for someone else
			participants_id = data.get('participants_id')
			if participants_id and str(participants_id) != str(user.user_id) and not (user.is_staff or user.is_superuser):
				return Response(
					{'error': 'You can only create conversations for yourself.'}, 
					status=status.HTTP_403_FORBIDDEN
				)

		serializer = self.get_serializer(data=data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
	
	def retrieve(self, request, *args, **kwargs):
		"""
		Retrieve a conversation with access control
		"""
		instance = self.get_object()
		user = request.user
		
		# Check if user has permission to view this conversation
		if not (user.is_staff or user.is_superuser or instance.participants == user):
			return Response(
				{'error': 'You do not have permission to view this conversation.'}, 
				status=status.HTTP_403_FORBIDDEN
			)
		
		serializer = self.get_serializer(instance)
		return Response(serializer.data)
	
	def update(self, request, *args, **kwargs):
		"""
		Update a conversation with access control
		"""
		instance = self.get_object()
		user = request.user
		
		# Check if user has permission to update this conversation
		if not (user.is_staff or user.is_superuser or instance.participants == user):
			return Response(
				{'error': 'You can only update your own conversation.'}, 
				status=status.HTTP_403_FORBIDDEN
			)
		
		return super().update(request, *args, **kwargs)
	
	def destroy(self, request, *args, **kwargs):
		"""
		Delete a conversation with access control
		"""
		instance = self.get_object()
		user = request.user
		
		# Check if user has permission to delete this conversation
		if not (user.is_staff or user.is_superuser or instance.participants == user):
			return Response(
				{'error': 'You can only delete your own conversation.'}, 
				status=status.HTTP_403_FORBIDDEN
			)
		
		return super().destroy(request, *args, **kwargs)


class MessageViewSet(viewsets.ModelViewSet):
	"""List and create messages for conversations.

	list: list messages (scoped to conversation or user's conversation)
	create: send a message to an existing conversation
	"""
	queryset = Message.objects.all().select_related('sender', 'conversation')
	serializer_class = MessageSerializer
	permission_classes = [IsParticipantOfConversation, CanManageOwnMessages]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_class = MessageFilter
	search_fields = ['message_body', 'sender__username', 'sender__email']
	ordering_fields = ['sent_at', 'edited_at']
	ordering = ['-sent_at']
	pagination_class = MessagePagination

	def get_queryset(self):
		"""
		Filter messages based on user permissions.
		Users can only access messages from conversations they participate in.
		"""
		user = self.request.user
		
		# Check if user is authenticated
		if not user.is_authenticated:
			return Message.objects.none()
		
		# Staff and superusers can see all messages
		if user.is_staff or user.is_superuser:
			qs = self.queryset
		else:
			# Regular users can only see messages from conversations they participate in
			qs = Message.objects.filter(conversation__participants=user).select_related('sender', 'conversation')
		
		# Apply conversation filtering if specified
		conversation_id = self.request.query_params.get('conversation')
		if conversation_id:
			# Verify user has access to this conversation
			try:
				conversation = Conversation.objects.get(conversation_id=conversation_id)
				if not (user.is_staff or user.is_superuser or conversation.participants == user):
					# User doesn't have permission to access this conversation
					return Message.objects.none()
				qs = qs.filter(conversation__conversation_id=conversation_id)
			except Conversation.DoesNotExist:
				return Message.objects.none()
		
		return qs.order_by('-sent_at')

	def create(self, request, *args, **kwargs):
		"""
		Create a new message with proper access control
		"""
		data = request.data.copy()
		user = request.user
		
		# If sender_id is not provided, use request.user
		if 'sender_id' not in data:
			data['sender_id'] = user.pk

		# Validate conversation access
		conversation_id = data.get('conversation')
		if conversation_id:
			try:
				conversation = Conversation.objects.get(conversation_id=conversation_id)
				# Check if user is participant of this conversation
				if not (user.is_staff or user.is_superuser or conversation.participants == user):
					return Response(
						{'error': 'You do not have permission to send messages to this conversation.'}, 
						status=status.HTTP_403_FORBIDDEN
					)
			except Conversation.DoesNotExist:
				return Response(
					{'conversation': 'Conversation not found.'}, 
					status=status.HTTP_400_BAD_REQUEST
				)
		else:
			# Try to find the user's conversation
			try:
				conversation = Conversation.objects.get(participants=user)
				data['conversation'] = conversation.conversation_id
			except Conversation.DoesNotExist:
				return Response(
					{'conversation': 'Conversation not found for user.'}, 
					status=status.HTTP_400_BAD_REQUEST
				)

		serializer = self.get_serializer(data=data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
	
	def retrieve(self, request, *args, **kwargs):
		"""
		Retrieve a message with access control
		"""
		instance = self.get_object()
		user = request.user
		
		# Check if user has permission to view this message
		if not (user.is_staff or user.is_superuser or instance.conversation.participants == user):
			return Response(
				{'error': 'You do not have permission to view this message.'}, 
				status=status.HTTP_403_FORBIDDEN
			)
		
		serializer = self.get_serializer(instance)
		return Response(serializer.data)
	
	def update(self, request, *args, **kwargs):
		"""
		Update a message with access control
		"""
		instance = self.get_object()
		user = request.user
		
		# Check if user has permission to update this message
		if not (user.is_staff or user.is_superuser or instance.sender == user):
			return Response(
				{'error': 'You can only edit your own messages.'}, 
				status=status.HTTP_403_FORBIDDEN
			)
		
		return super().update(request, *args, **kwargs)
	
	def destroy(self, request, *args, **kwargs):
		"""
		Delete a message with access control
		"""
		instance = self.get_object()
		user = request.user
		
		# Check if user has permission to delete this message
		if not (user.is_staff or user.is_superuser or instance.sender == user):
			return Response(
				{'error': 'You can only delete your own messages.'}, 
				status=status.HTTP_403_FORBIDDEN
			)
		
		return super().destroy(request, *args, **kwargs)
	
	@action(detail=False, methods=['get'])
	def my_messages(self, request):
		"""
		Get all messages from the current user's conversation with pagination and filtering
		"""
		user = request.user
		
		if not user.is_authenticated:
			return Response(
				{'error': 'Authentication required.'}, 
				status=status.HTTP_401_UNAUTHORIZED
			)
		
		# Get messages using explicit filtering
		messages = Message.objects.filter(
			conversation__participants=user
		).select_related('sender', 'conversation').order_by('-sent_at')
		
		# Apply additional filters if provided
		filterset = MessageFilter(request.GET, queryset=messages)
		if filterset.is_valid():
			messages = filterset.qs
		
		page = self.paginate_queryset(messages)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)
		
		serializer = self.get_serializer(messages, many=True)
		return Response(serializer.data)
	
	@action(detail=False, methods=['get'])
	def recent_messages(self, request):
		"""
		Get recent messages from the current user's conversation (last 24 hours)
		"""
		from datetime import timedelta
		from django.utils import timezone
		
		user = request.user
		
		if not user.is_authenticated:
			return Response(
				{'error': 'Authentication required.'}, 
				status=status.HTTP_401_UNAUTHORIZED
			)
		
		# Get messages from last 24 hours
		last_24_hours = timezone.now() - timedelta(hours=24)
		messages = Message.objects.filter(
			conversation__participants=user,
			sent_at__gte=last_24_hours
		).select_related('sender', 'conversation').order_by('-sent_at')
		
		page = self.paginate_queryset(messages)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)
		
		serializer = self.get_serializer(messages, many=True)
		return Response(serializer.data)
	
	@action(detail=False, methods=['get'])
	def search_messages(self, request):
		"""
		Search messages with advanced filtering and pagination
		"""
		user = request.user
		
		if not user.is_authenticated:
			return Response(
				{'error': 'Authentication required.'}, 
				status=status.HTTP_401_UNAUTHORIZED
			)
		
		# Base queryset
		queryset = Message.objects.filter(
			conversation__participants=user
		).select_related('sender', 'conversation')
		
		# Apply filters
		filterset = MessageFilter(request.GET, queryset=queryset)
		if filterset.is_valid():
			filtered_messages = filterset.qs.order_by('-sent_at')
		else:
			return Response(
				{'error': 'Invalid filter parameters', 'details': filterset.errors}, 
				status=status.HTTP_400_BAD_REQUEST
			)
		
		# Apply pagination
		page = self.paginate_queryset(filtered_messages)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			response_data = self.get_paginated_response(serializer.data)
			
			# Add filter information to response
			response_data.data['applied_filters'] = {
				key: value for key, value in request.GET.items()
				if value and key not in ['page', 'page_size']
			}
			return response_data
		
		serializer = self.get_serializer(filtered_messages, many=True)
		return Response({
			'results': serializer.data,
			'applied_filters': {
				key: value for key, value in request.GET.items()
				if value and key not in ['page', 'page_size']
			}
		})

