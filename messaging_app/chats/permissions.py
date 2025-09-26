from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission class to ensure only participants in a conversation 
    can send, view, update and delete messages in that conversation.
    Only allows authenticated users to access the API.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated before allowing any access
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission to only allow participants of a conversation 
        to access its messages.
        """
        # Staff and superusers have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # For Message objects, check if user is the conversation participant
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants == request.user
        
        # For Conversation objects, check if user is the participant
        if hasattr(obj, 'participants'):
            return obj.participants == request.user
        
        return False
    
    def get_queryset_filter(self, request, view):
        """
        Optional method to filter queryset based on user permissions
        """
        if request.user.is_staff or request.user.is_superuser:
            return {}
        return {'participants': request.user} if hasattr(view, 'get_queryset') else {}


class IsAuthenticatedAndParticipant(permissions.BasePermission):
    """
    Permission that requires authentication and ensures users can only 
    access conversations and messages they are participants in.
    """
    
    def has_permission(self, request, view):
        """Only allow authenticated users"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is participant of the conversation"""
        # Staff and superusers have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # For Message objects
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants == request.user
        
        # For Conversation objects  
        if hasattr(obj, 'participants'):
            return obj.participants == request.user
        
        return False


class CanManageOwnMessages(permissions.BasePermission):
    """
    Permission that allows users to manage their own messages within 
    conversations they participate in.
    """
    
    def has_permission(self, request, view):
        """Only allow authenticated users"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Allow users to:
        - View messages in conversations they participate in
        - Edit/Delete only their own messages
        """
        # Staff and superusers have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if user is participant in the conversation
        is_participant = obj.conversation.participants == request.user
        
        if not is_participant:
            return False
        
        # For safe methods (GET, HEAD, OPTIONS), allow if user is participant
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For unsafe methods (PUT, PATCH, DELETE), only allow message owner
        return obj.sender == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class IsOwnerOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own conversations.
    """
    
    def has_permission(self, request, view):
        # Allow authenticated users to list/create conversations
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff and superusers can access any conversation
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Regular users can only access their own conversation
        return obj.participants == request.user


class IsMessageOwnerOrConversationParticipant(permissions.BasePermission):
    """
    Custom permission for messages that allows:
    - Staff/superusers: full access
    - Message sender: full access to their own messages
    - Conversation participant: read access to all messages in their conversation
    """
    
    def has_permission(self, request, view):
        # Allow authenticated users
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff and superusers can access any message
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Message sender can modify their own messages
        if obj.sender == request.user:
            return True
        
        # Conversation participant can view messages in their conversation
        if request.method in permissions.SAFE_METHODS:
            return obj.conversation.participants == request.user
        
        return False


class IsAdminOrSelf(permissions.BasePermission):
    """
    Custom permission that allows users to only access their own profile,
    unless they are admin/staff.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff and superusers can access any user
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        # Users can only access their own profile
        return obj == request.user


class IsOwnerOfMessage(permissions.BasePermission):
    """
    Custom permission to only allow message senders to edit/delete their messages.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff and superusers have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # For safe methods (GET, HEAD, OPTIONS), allow if user is conversation participant
        if request.method in permissions.SAFE_METHODS:
            return obj.conversation.participants == request.user
        
        # For unsafe methods (POST, PUT, PATCH, DELETE), only allow message owner
        return obj.sender == request.user


class CanCreateConversation(permissions.BasePermission):
    """
    Custom permission that allows users to create conversations only for themselves,
    unless they are staff/admin.
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Allow staff/admin to create conversations for anyone
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # For regular users, check if they're trying to create for themselves
        if request.method == 'POST':
            participants_id = request.data.get('participants_id')
            if participants_id and str(participants_id) != str(request.user.user_id):
                return False
        
        return True