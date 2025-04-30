from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ProfileUpdateView, StudentParentListCreateView, StudentParentRetrieveUpdateDestroyView
)

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),

    path('student-parents/', StudentParentListCreateView.as_view(), name='student-parent-list-create'),
    path('student-parents/<int:pk>/', StudentParentRetrieveUpdateDestroyView.as_view(), name='student-parent-detail'),
]
