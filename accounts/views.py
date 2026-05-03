from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView

from .forms import RoleAuthenticationForm


User = get_user_model()


class RoleLoginView(LoginView):
    authentication_form = RoleAuthenticationForm
    template_name = "login.html"

    def get_initial(self):
        initial = super().get_initial()
        requested_role = self.request.GET.get("role")
        valid_roles = {User.TEACHER, User.CUSTOMER_ADMIN}
        initial["role"] = requested_role if requested_role in valid_roles else User.TEACHER
        return initial
