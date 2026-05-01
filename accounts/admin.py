from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Driving School", {"fields": ("role", "school")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Driving School", {"fields": ("role", "school")}),
    )
    list_display = ("username", "email", "role", "school", "is_active", "is_staff")
    list_filter = ("role", "school", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
