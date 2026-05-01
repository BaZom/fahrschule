from django.contrib import admin

from .models import MinuteEntry, WeeklyPool


@admin.register(WeeklyPool)
class WeeklyPoolAdmin(admin.ModelAdmin):
    list_display = ("school", "week_start", "total_minutes", "created_by", "created_at")
    list_filter = ("school", "week_start")
    search_fields = ("school__name", "created_by__username")


@admin.register(MinuteEntry)
class MinuteEntryAdmin(admin.ModelAdmin):
    list_display = ("school", "weekly_pool", "teacher", "minutes_used", "created_at")
    list_filter = ("school", "weekly_pool", "teacher")
    search_fields = ("teacher__username", "note")
