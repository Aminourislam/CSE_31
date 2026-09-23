from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_view, name='view'),
    path('edit/', views.profile_edit, name='edit'),
    path('settings/', views.privacy_settings, name='privacy'),

    # Password change
    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='profiles/change_password.html',
            success_url='/profile/change-password/done/',
        ),
        name='change_password',
    ),
    path(
        'change-password/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='profiles/change_password_done.html',
        ),
        name='change_password_done',
    ),

    # AJAX
    path('ajax/load-districts/', views.load_districts, name='ajax_districts'),
    path('ajax/load-upazilas/', views.load_upazilas, name='ajax_upazilas'),
]