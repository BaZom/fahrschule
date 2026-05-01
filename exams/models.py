from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class WeeklyPool(models.Model):
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, related_name="weekly_pools")
    week_start = models.DateField()
    total_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_weekly_pools",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["school", "week_start"], name="unique_weekly_pool_per_school")
        ]
        ordering = ["-week_start"]

    def __str__(self):
        return f"{self.school} - {self.week_start}"


class MinuteEntry(models.Model):
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, related_name="minute_entries")
    weekly_pool = models.ForeignKey(WeeklyPool, on_delete=models.CASCADE, related_name="entries")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="minute_entries",
    )
    minutes_used = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.teacher} - {self.minutes_used} min"
