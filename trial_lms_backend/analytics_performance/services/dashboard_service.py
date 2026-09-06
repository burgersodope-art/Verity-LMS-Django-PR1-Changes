# analytics_performance/services/dashboard_service.py

from django.db.models import Avg

from content_management.models import (
    ModuleProgress,
    LessonCompletion
)

from assessment_management.models import (
    AssessmentSubmission
)

from analytics_performance.models import (
    StudentDashboard
)


def refresh_student_dashboard(
    student
):

    submissions = (
        AssessmentSubmission.objects
        .filter(
            student=student
        )
    )

    average = (
        submissions.aggregate(
            avg=Avg(
                "percentage"
            )
        )["avg"] or 0
    )

    modules_completed = (
        ModuleProgress.objects
        .filter(
            student=student,
            is_completed=True
        )
        .count()
    )

    lessons_completed = (
        LessonCompletion.objects
        .filter(
            student=student,
            is_completed=True
        )
        .count()
    )

# >>> ADDED / CHANGED: Safely resolve school via SchoolUser and grade via student_profile to avoid AttributeError ('User' object has no attribute 'school')
    from schools.models import SchoolUser, School

    school_user = SchoolUser.objects.filter(user=student).first()
    school = school_user.school if school_user else School.objects.first()

    student_profile = getattr(student, "student_profile", None)
    grade = student_profile.grade if student_profile else None

    dashboard, _ = (
        StudentDashboard.objects
        .get_or_create(
            student=student,
            defaults={
                "school": school,
                "grade": grade,
            }
        )
    )

    dashboard.overall_average = (
        average
    )

    dashboard.total_assessments = (
        submissions.count()
    )

    dashboard.total_modules_completed = (
        modules_completed
    )

    dashboard.total_lessons_completed = (
        lessons_completed
    )

    dashboard.completion_rate = (
        average
    )

    dashboard.save()

    return dashboard


def get_student_dashboard(
    student
):

    dashboard = (
        StudentDashboard.objects
        .select_related(
            "grade"
        )
        .get(
            student=student
        )
    )

    return {
        "overall_average":
            dashboard.overall_average,

        "total_assessments":
            dashboard.total_assessments,

        "total_modules_completed":
            dashboard.total_modules_completed,

        "total_lessons_completed":
            dashboard.total_lessons_completed,

        "completion_rate":
            dashboard.completion_rate,

        "strengths":
            dashboard.strengths,

        "weaknesses":
            dashboard.weaknesses,

        "last_updated":
            dashboard.last_computed_at
    }
