from datetime import timedelta

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import MinuteEntry, WeeklyPool


def get_current_week_start(today=None):
    current_date = today or timezone.localdate()
    return current_date - timedelta(days=current_date.weekday())


def get_current_week_pool(school):
    return WeeklyPool.objects.filter(school=school, week_start=get_current_week_start()).first()


def get_pool_status(pool):
    used_minutes = pool.entries.aggregate(total=Sum("minutes_used"))["total"] or 0
    return {
        "total_minutes": pool.total_minutes,
        "used_minutes": used_minutes,
        "remaining_minutes": pool.total_minutes - used_minutes,
    }


def validate_weekly_pool_update(pool, new_total_minutes):
    if new_total_minutes <= 0:
        raise ValueError("Total minutes must be greater than 0.")

    used_minutes = pool.entries.aggregate(total=Sum("minutes_used"))["total"] or 0
    if new_total_minutes < used_minutes:
        raise ValueError("Total minutes cannot be lower than already used minutes.")


def register_minutes(*, teacher, weekly_pool_id, minutes_used, note=""):
    if minutes_used <= 0:
        raise ValueError("Minutes used must be greater than 0.")

    if teacher.school_id is None:
        raise ValueError("Teacher must belong to a school.")

    with transaction.atomic():
        pool = WeeklyPool.objects.select_for_update().get(pk=weekly_pool_id)

        if pool.school_id != teacher.school_id:
            raise ValueError("Teachers can only register minutes for their own school.")

        used_minutes = (
            MinuteEntry.objects.filter(weekly_pool=pool).aggregate(total=Sum("minutes_used"))["total"] or 0
        )
        if used_minutes + minutes_used > pool.total_minutes:
            remaining = pool.total_minutes - used_minutes
            raise ValueError(f"Not enough minutes remain. Remaining minutes: {remaining}.")

        return MinuteEntry.objects.create(
            school=pool.school,
            weekly_pool=pool,
            teacher=teacher,
            minutes_used=minutes_used,
            note=note,
        )


def update_minute_entry(*, entry, minutes_used, note=""):
    if minutes_used <= 0:
        raise ValueError("Minutes used must be greater than 0.")

    with transaction.atomic():
        locked_entry = MinuteEntry.objects.select_for_update().select_related("weekly_pool").get(pk=entry.pk)
        pool = WeeklyPool.objects.select_for_update().get(pk=locked_entry.weekly_pool_id)
        used_other_minutes = (
            MinuteEntry.objects.filter(weekly_pool=pool)
            .exclude(pk=locked_entry.pk)
            .aggregate(total=Sum("minutes_used"))["total"]
            or 0
        )

        if used_other_minutes + minutes_used > pool.total_minutes:
            remaining = pool.total_minutes - used_other_minutes
            raise ValueError(f"Not enough minutes remain. Maximum allowed for this entry: {remaining}.")

        locked_entry.minutes_used = minutes_used
        locked_entry.note = note
        locked_entry.save(update_fields=["minutes_used", "note"])
        return locked_entry
