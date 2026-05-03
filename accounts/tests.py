from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from schools.models import School


User = get_user_model()


class RoleLoginTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Demo Driving School")
        self.teacher = User.objects.create_user(
            username="teacher",
            password="pass",
            role=User.TEACHER,
            school=self.school,
        )
        self.manager = User.objects.create_user(
            username="manager",
            password="pass",
            role=User.CUSTOMER_ADMIN,
            school=self.school,
        )

    def test_teacher_can_login_as_teacher(self):
        response = self.client.post(
            reverse("login"),
            {"username": "teacher", "password": "pass", "role": User.TEACHER},
        )

        self.assertRedirects(response, reverse("dashboard"), fetch_redirect_response=False)

    def test_teacher_cannot_login_as_school_manager(self):
        response = self.client.post(
            reverse("login"),
            {"username": "teacher", "password": "pass", "role": User.CUSTOMER_ADMIN},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This account cannot log in as the selected role")

    def test_school_manager_can_login_as_school_manager(self):
        response = self.client.post(
            reverse("login"),
            {"username": "manager", "password": "pass", "role": User.CUSTOMER_ADMIN},
        )

        self.assertRedirects(response, reverse("dashboard"), fetch_redirect_response=False)
