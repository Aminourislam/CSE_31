from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('pending-users/', views.pending_users, name='pending_users'),

    # Actions
    path('users/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    path('users/<int:user_id>/reject/', views.reject_user, name='reject_user'),
    path('users/<int:user_id>/suspend/', views.suspend_user, name='suspend_user'),
    path('users/<int:user_id>/restore/', views.restore_user, name='restore_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
]