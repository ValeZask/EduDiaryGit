from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('chats/', views.ChatListCreateView.as_view(), name='chat-list-create'),
    path('chats/<int:chat_id>/messages/', views.ChatMessageListCreateView.as_view(), name='chat-messages'),
    path('messages/unread/', views.UnreadMessageListView.as_view(), name='unread-messages'),
]