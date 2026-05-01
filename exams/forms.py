from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import MinuteEntry, WeeklyPool
from .services import validate_weekly_pool_update


User = get_user_model()


class MinuteEntryForm(forms.ModelForm):
    class Meta:
        model = MinuteEntry
        fields = ["weekly_pool", "minutes_used", "note"]
        widgets = {"note": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school is not None:
            self.fields["weekly_pool"].queryset = WeeklyPool.objects.filter(school=school)


class WeeklyPoolForm(forms.ModelForm):
    class Meta:
        model = WeeklyPool
        fields = ["week_start", "total_minutes"]
        widgets = {"week_start": forms.DateInput(attrs={"type": "date"})}

    def clean(self):
        cleaned_data = super().clean()
        total_minutes = cleaned_data.get("total_minutes")
        if self.instance.pk and total_minutes is not None:
            try:
                validate_weekly_pool_update(self.instance, total_minutes)
            except ValueError as exc:
                self.add_error("total_minutes", str(exc))
        return cleaned_data


class TeacherCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")


class TeacherUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active")
