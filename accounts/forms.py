from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class RoleAuthenticationForm(AuthenticationForm):
    role = forms.ChoiceField(
        choices=(
            (User.TEACHER, "Teacher"),
            (User.CUSTOMER_ADMIN, "School Manager"),
        ),
        widget=forms.RadioSelect,
        initial=User.TEACHER,
    )

    error_messages = {
        **AuthenticationForm.error_messages,
        "role_mismatch": _(
            "This account cannot log in as the selected role. Choose the correct login type."
        ),
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        selected_role = self.cleaned_data.get("role")
        if selected_role and user.role != selected_role:
            raise ValidationError(
                self.error_messages["role_mismatch"],
                code="role_mismatch",
            )
