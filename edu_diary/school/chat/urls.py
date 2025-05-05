from django.urls import path
from .views import (
    ChatListCreateView,
    ChatRetrieveView,
    ChatMessageListCreateView,
    ChatParticipantListView,
    MarkAllMessagesAsReadView,
    AddChatParticipantView, ChatSearchView,
)

app_name = 'chat'

urlpatterns = [
    path('chats/', ChatListCreateView.as_view(), name='chat-list-create'),

    path('chats/<int:pk>/', ChatRetrieveView.as_view(), name='chat-detail'),
    path('chats/search/', ChatSearchView.as_view(), name='chat-search'),
    path('chats/<int:chat_id>/messages/', ChatMessageListCreateView.as_view(), name='chat-messages'),
    path('chats/<int:chat_id>/read/', MarkAllMessagesAsReadView.as_view(), name='mark-read'),

    path('chats/<int:chat_id>/participants/', ChatParticipantListView.as_view(), name='chat-participants'),
    path('chats/<int:chat_id>/participants/add/', AddChatParticipantView.as_view(), name='chat-add-participant'),
]

