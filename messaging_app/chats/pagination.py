from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict


class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages with 20 items per page
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Custom paginated response with additional metadata
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.page_size),
            ('results', data)
        ]))


class ConversationPagination(PageNumberPagination):
    """
    Custom pagination class for conversations
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Custom paginated response with additional metadata
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.page_size),
            ('results', data)
        ]))


class StandardResultsPagination(PageNumberPagination):
    """
    Standard pagination class for general use
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class LargeResultsPagination(PageNumberPagination):
    """
    Pagination class for large result sets
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    page_query_param = 'page'


class SmallResultsPagination(PageNumberPagination):
    """
    Pagination class for small result sets
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'


class MessageLimitOffsetPagination(LimitOffsetPagination):
    """
    Alternative pagination using limit/offset for messages
    """
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100
    
    def get_paginated_response(self, data):
        """
        Custom paginated response with additional metadata
        """
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('limit', self.limit),
            ('offset', self.offset),
            ('results', data)
        ]))


class CustomMessagePagination(PageNumberPagination):
    """
    Enhanced pagination specifically for messages with conversation context
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Enhanced paginated response with message-specific metadata
        """
        # Calculate additional statistics if needed
        response_data = OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('has_next', self.page.has_next()),
            ('has_previous', self.page.has_previous()),
            ('results', data)
        ])
        
        # Add conversation context if available
        if hasattr(self, 'conversation_id'):
            response_data['conversation_id'] = self.conversation_id
        
        return Response(response_data)
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        Override to store conversation context
        """
        # Store conversation ID if filtering by conversation
        conversation_id = request.query_params.get('conversation_id')
        if conversation_id:
            self.conversation_id = conversation_id
        
        return super().paginate_queryset(queryset, request, view)