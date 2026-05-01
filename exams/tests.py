from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from schools.models import School

from .models import MinuteEntry, WeeklyPool
from .services import register_minutes, update_minute_entry, validate_weekly_pool_update


User = get_user_model()


class ExamMinuteTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Main Driving School")
        self.other_school = School.objects.create(name="Other Driving School")
        self.admin = User.objects.create_user(
            username="admin",
            password="pass",
            role=User.CUSTOMER_ADMIN,
            school=self.school,
        )
        self.other_admin = User.objects.create_user(
            username="other-admin",
            password="pass",
            role=User.CUSTOMER_ADMIN,
            school=self.other_school,
        )
        self.teacher = User.objects.create_user(
            username="teacher",
            password="pass",
            role=User.TEACHER,
            school=self.school,
        )
        self.other_teacher = User.objects.create_user(
            username="other-teacher",
            password="pass",
            role=User.TEACHER,
            school=self.other_school,
        )
        self.pool = WeeklyPool.objects.create(
            school=self.school,
            week_start=date(2026, 4, 27),
            total_minutes=100,
            created_by=self.admin,
        )
        self.other_pool = WeeklyPool.objects.create(
            school=self.other_school,
            week_start=date(2026, 4, 27),
            total_minutes=100,
            created_by=self.other_admin,
        )

    def test_teacher_can_register_valid_minutes(self):
        entry = register_minutes(
            teacher=self.teacher,
            weekly_pool_id=self.pool.id,
            minutes_used=30,
            note="Exam A",
        )

        self.assertEqual(entry.school, self.school)
        self.assertEqual(entry.teacher, self.teacher)
        self.assertEqual(entry.minutes_used, 30)

    def test_teacher_cannot_exceed_remaining_minutes(self):
        register_minutes(teacher=self.teacher, weekly_pool_id=self.pool.id, minutes_used=80)

        with self.assertRaisesMessage(ValueError, "Not enough minutes remain"):
            register_minutes(teacher=self.teacher, weekly_pool_id=self.pool.id, minutes_used=25)

    def test_two_registrations_cannot_exceed_pool_total(self):
        first = register_minutes(teacher=self.teacher, weekly_pool_id=self.pool.id, minutes_used=60)

        with self.assertRaisesMessage(ValueError, "Not enough minutes remain"):
            register_minutes(teacher=self.teacher, weekly_pool_id=self.pool.id, minutes_used=50)

        self.assertEqual(MinuteEntry.objects.filter(weekly_pool=self.pool).count(), 1)
        self.assertEqual(first.minutes_used, 60)

    def test_teacher_cannot_register_against_another_schools_pool(self):
        with self.assertRaisesMessage(ValueError, "own school"):
            register_minutes(teacher=self.teacher, weekly_pool_id=self.other_pool.id, minutes_used=10)

    def test_customer_admin_cannot_reduce_weekly_total_below_used_minutes(self):
        register_minutes(teacher=self.teacher, weekly_pool_id=self.pool.id, minutes_used=70)

        with self.assertRaisesMessage(ValueError, "already used"):
            validate_weekly_pool_update(self.pool, 60)

    def test_entry_correction_cannot_exceed_pool_total(self):
        entry = register_minutes(teacher=self.teacher, weekly_pool_id=self.pool.id, minutes_used=90)

        with self.assertRaisesMessage(ValueError, "Not enough minutes remain"):
            update_minute_entry(entry=entry, minutes_used=120, note="")

    def test_teacher_cannot_access_admin_pages(self):
        self.client.login(username="teacher", password="pass")

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_customer_admin_only_sees_own_school_data(self):
        MinuteEntry.objects.create(
            school=self.school,
            weekly_pool=self.pool,
            teacher=self.teacher,
            minutes_used=20,
            note="own entry",
        )
        MinuteEntry.objects.create(
            school=self.other_school,
            weekly_pool=self.other_pool,
            teacher=self.other_teacher,
            minutes_used=20,
            note="other entry",
        )
        self.client.login(username="admin", password="pass")

        response = self.client.get(reverse("admin_dashboard"))

        self.assertContains(response, "own entry")
        self.assertNotContains(response, "other entry")
        self.assertContains(response, "teacher")
        self.assertNotContains(response, "other-teacher")
