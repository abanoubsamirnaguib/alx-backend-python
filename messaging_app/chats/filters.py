import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Message, Conversation, User


class MessageFilter(filters.FilterSet):
    """
    Filter class for Message model to retrieve messages with specific criteria
    including conversations with specific users or messages within a time range
    """
    
    # Filter by conversation participant (user)
    participant = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='conversation__participants',
        help_text='Filter messages by conversation participant'
    )
    
    # Filter by conversation participant username
    participant_username = filters.CharFilter(
        field_name='conversation__participants__username',
        lookup_expr='icontains',
        help_text='Filter messages by participant username (case insensitive)'
    )
    
    # Filter by message sender
    sender = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='sender',
        help_text='Filter messages by sender'
    )
    
    # Filter by sender username
    sender_username = filters.CharFilter(
        field_name='sender__username',
        lookup_expr='icontains',
        help_text='Filter messages by sender username (case insensitive)'
    )
    
    # Time range filters
    sent_after = filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        help_text='Filter messages sent after this datetime (YYYY-MM-DD HH:MM:SS)'
    )
    
    sent_before = filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        help_text='Filter messages sent before this datetime (YYYY-MM-DD HH:MM:SS)'
    )
    
    # Date range filter
    sent_date = filters.DateFilter(
        field_name='sent_at__date',
        help_text='Filter messages sent on specific date (YYYY-MM-DD)'
    )
    
    # Filter by message content
    message_content = filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains',
        help_text='Filter messages containing specific text (case insensitive)'
    )
    
    # Filter by system messages
    is_system_message = filters.BooleanFilter(
        field_name='is_from_system',
        help_text='Filter by system messages (true) or user messages (false)'
    )
    
    # Filter by deleted messages
    include_deleted = filters.BooleanFilter(
        method='filter_deleted_messages',
        help_text='Include deleted messages in results (default: false)'
    )
    
    # Custom date range filter
    date_range = filters.CharFilter(
        method='filter_date_range',
        help_text='Filter messages within date range. Options: today, yesterday, last_week, last_month'
    )
    
    # Filter by conversation ID
    conversation_id = filters.UUIDFilter(
        field_name='conversation__conversation_id',
        help_text='Filter messages by conversation ID'
    )
    
    def filter_deleted_messages(self, queryset, name, value):
        """
        Custom filter method to include/exclude deleted messages
        """
        if not value:
            # Exclude deleted messages by default
            return queryset.filter(is_deleted=False)
        return queryset
    
    def filter_date_range(self, queryset, name, value):
        """
        Custom filter method for predefined date ranges
        """
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        now = timezone.now()
        
        if value == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return queryset.filter(sent_at__gte=start_date)
        elif value == 'yesterday':
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            return queryset.filter(sent_at__gte=start_date, sent_at__lt=end_date)
        elif value == 'last_week':
            start_date = now - timedelta(days=7)
            return queryset.filter(sent_at__gte=start_date)
        elif value == 'last_month':
            start_date = now - timedelta(days=30)
            return queryset.filter(sent_at__gte=start_date)
        
        return queryset
    
    class Meta:
        model = Message
        fields = {
            'sent_at': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'edited_at': ['exact', 'isnull'],
            'is_deleted': ['exact'],
            'is_from_system': ['exact'],
        }


class ConversationFilter(filters.FilterSet):
    """
    Filter class for Conversation model
    """
    
    # Filter by participant
    participant = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='participants',
        help_text='Filter conversations by participant'
    )
    
    # Filter by participant username
    participant_username = filters.CharFilter(
        field_name='participants__username',
        lookup_expr='icontains',
        help_text='Filter conversations by participant username'
    )
    
    # Filter by participant email
    participant_email = filters.CharFilter(
        field_name='participants__email',
        lookup_expr='icontains',
        help_text='Filter conversations by participant email'
    )
    
    # Time range filters
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter conversations created after this datetime'
    )
    
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter conversations created before this datetime'
    )
    
    # Filter conversations with messages
    has_messages = filters.BooleanFilter(
        method='filter_has_messages',
        help_text='Filter conversations that have messages'
    )
    
    # Filter by conversation activity
    updated_after = filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte',
        help_text='Filter conversations updated after this datetime'
    )
    
    def filter_has_messages(self, queryset, name, value):
        """
        Filter conversations based on whether they have messages
        """
        if value:
            return queryset.filter(messages__isnull=False).distinct()
        else:
            return queryset.filter(messages__isnull=True)
    
    class Meta:
        model = Conversation
        fields = {
            'created_at': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'updated_at': ['exact', 'lt', 'gt', 'lte', 'gte'],
        }


class UserFilter(filters.FilterSet):
    """
    Filter class for User model (for admin/staff use)
    """
    
    # Filter by role
    role = filters.ChoiceFilter(
        choices=User.ROLE_CHOICES,
        help_text='Filter users by role'
    )
    
    # Filter by name
    name = filters.CharFilter(
        method='filter_by_name',
        help_text='Filter users by first name or last name'
    )
    
    # Filter by registration date
    registered_after = filters.DateFilter(
        field_name='created_at__date',
        lookup_expr='gte',
        help_text='Filter users registered after this date'
    )
    
    registered_before = filters.DateFilter(
        field_name='created_at__date',
        lookup_expr='lte',
        help_text='Filter users registered before this date'
    )
    
    def filter_by_name(self, queryset, name, value):
        """
        Filter users by first name or last name
        """
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )
    
    class Meta:
        model = User
        fields = {
            'username': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_staff': ['exact'],
            'created_at': ['exact', 'lt', 'gt', 'lte', 'gte'],
        }