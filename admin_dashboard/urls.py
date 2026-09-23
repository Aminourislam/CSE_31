from django.urls import path
from . import views, event_views, announcement_views
from . import views, event_views, announcement_views, export_views
from . import views, event_views, announcement_views, export_views, import_views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('pending-users/', views.pending_users, name='pending_users'),

    # User actions
    path('users/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    path('users/<int:user_id>/reject/', views.reject_user, name='reject_user'),
    path('users/<int:user_id>/suspend/', views.suspend_user, name='suspend_user'),
    path('users/<int:user_id>/restore/', views.restore_user, name='restore_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),

    # Events
    path('events/', event_views.events_list, name='events_list'),
    path('events/create/', event_views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', event_views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', event_views.event_delete, name='event_delete'),
    path('events/<int:pk>/participants/', event_views.event_participants, name='event_participants'),
    path('events/<int:pk>/participants/export/', event_views.event_participants_export, name='event_participants_export'),  # ← new
    
    # Announcements
    path('announcements/', announcement_views.announcements_list, name='announcements_list'),
    path('announcements/create/', announcement_views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/edit/', announcement_views.announcement_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', announcement_views.announcement_delete, name='announcement_delete'),
    path('announcements/<int:pk>/toggle-publish/', announcement_views.announcement_toggle_publish, name='announcement_toggle_publish'),

    # Export
    path('export/', export_views.export_members, name='export'),
    # Import
    path('import/', import_views.import_members, name='import_members'),
]