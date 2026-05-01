from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from exams import views as exam_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", exam_views.dashboard_redirect, name="dashboard"),
    path("teacher/", exam_views.teacher_dashboard, name="teacher_dashboard"),
    path("admin-dashboard/", exam_views.admin_dashboard, name="admin_dashboard"),
    path("pools/new/", exam_views.weekly_pool_create, name="weekly_pool_create"),
    path("pools/<int:pk>/edit/", exam_views.weekly_pool_update, name="weekly_pool_update"),
    path("teachers/new/", exam_views.teacher_create, name="teacher_create"),
    path("teachers/<int:pk>/edit/", exam_views.teacher_update, name="teacher_update"),
    path("teachers/<int:pk>/deactivate/", exam_views.teacher_deactivate, name="teacher_deactivate"),
    path("entries/", exam_views.entries_history, name="entries_history"),
    path("entries/<int:pk>/edit/", exam_views.entry_update, name="entry_update"),
    path("entries/<int:pk>/delete/", exam_views.entry_delete, name="entry_delete"),
]
