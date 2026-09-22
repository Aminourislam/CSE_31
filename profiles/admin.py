from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'student_id', 'department', 'session']
    list_filter = ['university', 'department', 'session', 'batch', 'district']
    search_fields = ['full_name', 'student_id', 'user__email', 'phone']
    raw_id_fields = ['user']