from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = User
        fields = ('user_id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'created_at', 'password')
        read_only_fields = ('user_id', 'created_at')
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(write_only=True, source='sender', queryset=User.objects.all())
    class Meta:
        model = Message
        fields = ('message_id', 'sender', 'sender_id', 'conversation', 'message_body', 'sent_at', 'edited_at', 'is_deleted', 'is_from_system')
        read_only_fields = ('message_id', 'sent_at', 'edited_at')
    def create(self, validated_data):
        if 'sender' not in validated_data or validated_data.get('sender') is None:
            request = self.context.get('request') if self.context else None
            if request and hasattr(request, 'user') and not request.user.is_anonymous:
                validated_data['sender'] = request.user
            else:
                raise serializers.ValidationError("Sender must be provided or request.user must be authenticated.")
        return super().create(validated_data)

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(read_only=True)
    participants_id = serializers.PrimaryKeyRelatedField(write_only=True, source='participants', queryset=User.objects.all())
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Conversation
        fields = ('conversation_id', 'participants', 'participants_id', 'created_at', 'updated_at', 'messages')
        read_only_fields = ('conversation_id', 'created_at', 'updated_at')
    def create(self, validated_data):
        participants = validated_data.get('participants')
        from .models import Conversation as Conv
        if participants and Conv.objects.filter(participants=participants).exists():
            raise serializers.ValidationError({'participants': 'User already has a conversation.'})
        return super().create(validated_data)
