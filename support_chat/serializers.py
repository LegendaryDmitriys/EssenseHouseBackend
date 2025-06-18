from rest_framework import serializers
from support_chat.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['message', 'sender', 'is_admin', 'timestamp']
