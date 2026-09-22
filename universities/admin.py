from django.contrib import admin
from .models import University, Department, Session, Batch


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'is_active']
    search_fields = ['name', 'short_name']
    list_filter = ['is_active']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'university', 'is_active']
    list_filter = ['university', 'is_active']
    search_fields = ['name']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'session']
    list_filter = ['department__university', 'department', 'session']
    search_fields = ['name']