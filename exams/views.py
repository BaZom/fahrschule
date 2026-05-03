from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MinuteEntryForm, TeacherCreateForm, TeacherUpdateForm, WeeklyPoolForm
from .models import MinuteEntry, WeeklyPool
from .services import get_current_week_pool, get_pool_status, register_minutes, update_minute_entry


User = get_user_model()


def get_school_pool_cards(school):
    pools = WeeklyPool.objects.filter(school=school).select_related("created_by")[:12]
    return [{"pool": pool, "status": get_pool_status(pool)} for pool in pools]


def customer_admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_customer_admin():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def teacher_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_teacher():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
def dashboard_redirect(request):
    if request.user.is_customer_admin():
        return redirect("admin_dashboard")
    return redirect("teacher_dashboard")


@teacher_required
def teacher_dashboard(request):
    pool = get_current_week_pool(request.user.school)
    status = get_pool_status(pool) if pool else None
    recent_entries = MinuteEntry.objects.filter(school=request.user.school, teacher=request.user).select_related(
        "weekly_pool"
    )[:10]

    form = MinuteEntryForm(request.POST or None, school=request.user.school)
    if pool:
        form.fields["weekly_pool"].queryset = WeeklyPool.objects.filter(pk=pool.pk)
        form.fields["weekly_pool"].initial = pool
    if request.method == "POST":
        if not pool:
            messages.error(request, "No weekly pool exists for the current week.")
        elif form.is_valid():
            try:
                register_minutes(
                    teacher=request.user,
                    weekly_pool_id=form.cleaned_data["weekly_pool"].id,
                    minutes_used=form.cleaned_data["minutes_used"],
                    note=form.cleaned_data["note"],
                )
            except ValueError as exc:
                form.add_error(None, str(exc))
            else:
                messages.success(request, "Minutes registered.")
                return redirect("teacher_dashboard")

    return render(
        request,
        "teacher_dashboard.html",
        {"pool": pool, "status": status, "form": form, "recent_entries": recent_entries},
    )


@customer_admin_required
def admin_dashboard(request):
    school = request.user.school
    teachers = User.objects.filter(school=school, role=User.TEACHER).order_by("username")
    entries = MinuteEntry.objects.filter(school=school).select_related("teacher", "weekly_pool")[:25]

    return render(
        request,
        "admin_dashboard.html",
        {"pool_cards": get_school_pool_cards(school), "teachers": teachers, "entries": entries},
    )


@customer_admin_required
def weekly_pool_create(request):
    form = WeeklyPoolForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pool = form.save(commit=False)
        pool.school = request.user.school
        pool.created_by = request.user
        pool.save()
        messages.success(request, "Weekly pool created.")
        return redirect("admin_dashboard")

    return render(request, "weekly_pool_form.html", {"form": form, "title": "Create weekly pool"})


@customer_admin_required
def weekly_pool_update(request, pk):
    pool = get_object_or_404(WeeklyPool, pk=pk, school=request.user.school)
    form = WeeklyPoolForm(request.POST or None, instance=pool)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Weekly pool updated.")
        return redirect("admin_dashboard")

    return render(request, "weekly_pool_form.html", {"form": form, "title": "Edit weekly pool"})


@customer_admin_required
def teacher_create(request):
    form = TeacherCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        teacher = form.save(commit=False)
        teacher.school = request.user.school
        teacher.role = User.TEACHER
        teacher.save()
        messages.success(request, "Teacher created.")
        return redirect("admin_dashboard")

    return render(request, "teacher_form.html", {"form": form, "title": "Create teacher"})


@customer_admin_required
def teacher_update(request, pk):
    teacher = get_object_or_404(User, pk=pk, school=request.user.school, role=User.TEACHER)
    form = TeacherUpdateForm(request.POST or None, instance=teacher)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Teacher updated.")
        return redirect("admin_dashboard")

    return render(request, "teacher_form.html", {"form": form, "title": "Edit teacher"})


@customer_admin_required
def teacher_deactivate(request, pk):
    teacher = get_object_or_404(User, pk=pk, school=request.user.school, role=User.TEACHER)
    if request.method == "POST":
        teacher.is_active = False
        teacher.save(update_fields=["is_active"])
        messages.success(request, "Teacher deactivated.")
    return redirect("admin_dashboard")


@customer_admin_required
def entries_history(request):
    entries = MinuteEntry.objects.filter(school=request.user.school).select_related("teacher", "weekly_pool")
    return render(request, "entries_history.html", {"entries": entries})


@customer_admin_required
def entry_update(request, pk):
    entry = get_object_or_404(MinuteEntry, pk=pk, school=request.user.school)
    form = MinuteEntryForm(request.POST or None, instance=entry, school=request.user.school)
    form.fields["weekly_pool"].disabled = True
    if request.method == "POST" and form.is_valid():
        try:
            update_minute_entry(
                entry=entry,
                minutes_used=form.cleaned_data["minutes_used"],
                note=form.cleaned_data["note"],
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Entry updated.")
            return redirect("entries_history")

    return render(request, "weekly_pool_form.html", {"form": form, "title": "Correct minute entry"})


@customer_admin_required
def entry_delete(request, pk):
    entry = get_object_or_404(MinuteEntry, pk=pk, school=request.user.school)
    if request.method == "POST":
        entry.delete()
        messages.success(request, "Entry deleted.")
        return redirect("entries_history")
    return render(request, "confirm_delete.html", {"object": entry, "title": "Delete minute entry"})
