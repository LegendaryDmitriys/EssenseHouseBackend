from django.urls import path
from support_chat.views import ChatHistoryView

urlpatterns = [
    path('chat-messages/<int:question_id>/', ChatHistoryView.as_view(), name='chat-messages'),
]

