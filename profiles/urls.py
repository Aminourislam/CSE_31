from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_view, name='view'),
    path('edit/', views.profile_edit, name='edit'),
    path('settings/', views.privacy_settings, name='privacy'),

    # AJAX
    path('ajax/load-districts/', views.load_districts, name='ajax_districts'),
    path('ajax/load-upazilas/', views.load_upazilas, name='ajax_upazilas'),
]