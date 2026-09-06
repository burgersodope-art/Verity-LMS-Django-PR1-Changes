# services/dashboard_service.py

from django.db.models import Count

from content_management.models import (
    Chapter,
    Module,
    LessonCompletion,
    StudentDashboard,
    TeacherDashboard
)
## Admin Dashboard Views
def admin_dashboard():

    return {
        "chapters": Chapter.objects.count(),
        "modules": Module.objects.count(),
        "published_modules":
            Module.objects.filter(
                is_published=True
            ).count(),
        "lesson_completions":
            LessonCompletion.objects.filter(
                is_completed=True
            ).count()
    }

## student dashboard service

def get_student_dashboard(
    user
):
    dashboard, _ = (
        StudentDashboard.objects
        .get_or_create(student=user)
    )

    return {
        "completed_lessons":
            dashboard.completed_lessons,

        "pending_lessons":
            dashboard.pending_lessons,

        "completion_rate":
            dashboard.completion_rate,
    }

## teacher dashboard service

# >>> ADDED / CHANGED: Added get_teacher_dashboard service helper to fetch precomputed TeacherDashboard database metrics
def get_teacher_dashboard(
    user
):
    dashboard, _ = (
        TeacherDashboard.objects
        .get_or_create(teacher=user)
    )

    return {
        "modules_published":
            dashboard.modules_published,

        "students_impacted":
            dashboard.students_impacted,

        "average_completion_rate":
            float(dashboard.average_completion_rate),
    }
