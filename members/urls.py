from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.directory, name='directory'),
    path('<int:pk>/', views.member_detail, name='detail'),
]