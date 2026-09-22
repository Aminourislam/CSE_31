from django.contrib import admin
from .models import Division, District, Upazila


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'bn_name']
    search_fields = ['name']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'division']
    list_filter = ['division']
    search_fields = ['name']


@admin.register(Upazila)
class UpazilaAdmin(admin.ModelAdmin):
    list_display = ['name', 'district']
    list_filter = ['district__division', 'district']
    search_fields = ['name']