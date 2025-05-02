from django.urls import path
from .views import CategoryViewSet, NewsListView , NewsCreateUpdateView


app_name = 'news'

urlpatterns = [
    path('categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category-list-create'),
    path('categories/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='category-detail'),
    path('list/', NewsListView.as_view(), name='news-list'),
    path('create/', NewsCreateUpdateView.as_view(), name='news-create'),
]
