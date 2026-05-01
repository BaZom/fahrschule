from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    CUSTOMER_ADMIN = "customer_admin"
    TEACHER = "teacher"

    ROLE_CHOICES = [
        (CUSTOMER_ADMIN, "Customer Admin"),
        (TEACHER, "Teacher"),
    ]

    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default=TEACHER)
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )

    def is_customer_admin(self):
        return self.role == self.CUSTOMER_ADMIN

    def is_teacher(self):
        return self.role == self.TEACHER
