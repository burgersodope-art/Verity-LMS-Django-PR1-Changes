"""
content_management/tasks.py

Background jobs for:

1. Teacher cache warming
2. Teacher cache invalidation
3. Student dashboard refresh
4. Module completion statistics
5. Lesson completion processing
6. Progress recalculation
7. Scheduled analytics generation

These tasks are intentionally idempotent and safe to retry.
"""

from celery import shared_task
import logging


from django.db import transaction
from django.db.models import Count

from content_management.services.cache_service import (
    CacheService
)

logger = logging.getLogger(__name__)


# ==========================================================
# Teacher Cache Tasks
# ==========================================================

## clear Cache
@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def refresh_teacher_content_cache_task(
    self,
    teacher_id
):
    """
    Production cache refresh workflow.

    Steps:
        1. Clear cache
        2. Rebuild cache
    """

    from users.models import User

    teacher = User.objects.get(
        pk=teacher_id
    )

    CacheService.clear_teacher_cache(
        teacher_id
    )

    CacheService.get_teacher_chapters(
        teacher
    )

    CacheService.get_teacher_modules(
        teacher
    )

    logger.info(
        "Teacher cache refreshed. teacher_id=%s",
        teacher_id
    )

    return {
        "teacher_id": teacher_id,
        "status": "cache_refreshed",
    }
# ==========================================================
# Student Dashboard Refresh
# ==========================================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def refresh_student_dashboard_task(
    self,
    student_id
):
    """
    Recalculate dashboard metrics.

    Trigger after:
    - lesson completion
    - lesson uncompletion
    - module completion
    - new lesson created by teacher

    Dashboard reads become O(1)
    because values are precomputed.
    """

    from users.models import User
    from academics.models import StudentSubjectEnrollment

    from content_management.models import (
        StudentDashboard,
        LessonCompletion,
        LessonContent
    )

    student = (
        User.objects
        .get(pk=student_id)
    )

    total_completed = (
        LessonCompletion.objects
        .filter(
            student=student,
            is_completed=True
        )
        .count()
    )

    # >>> ADDED / CHANGED: Scope total published lessons to the student's enrolled subjects
    student_profile = getattr(student, "student_profile", None)
    if student_profile:
        enrolled_subject_ids = (
            StudentSubjectEnrollment.objects
            .filter(student=student_profile)
            .values_list("subject_id", flat=True)
        )
    else:
        enrolled_subject_ids = []

    if enrolled_subject_ids:
        total_lessons = (
            LessonContent.objects
            .filter(
                module__chapter__subject_id__in=enrolled_subject_ids,
                module__is_published=True
            )
            .distinct()
            .count()
        )
    else:
        total_lessons = (
            LessonContent.objects
            .filter(
                module__is_published=True
            )
            .count()
        )

    # >>> ADDED: Ensure total_lessons is bounded by completed count
    total_lessons = max(
        total_lessons,
        LessonCompletion.objects.filter(student=student).count(),
        total_completed
    )

    pending_lessons = max(0, total_lessons - total_completed)

    completion_rate = 0

    if total_lessons > 0:
        completion_rate = round(
            (
                total_completed /
                total_lessons
            ) * 100,
            2
        )

    StudentDashboard.objects.update_or_create(
        student=student,
        defaults={
            "completed_lessons":
                total_completed,

            "pending_lessons":
                pending_lessons,

            "completion_rate":
                completion_rate,
        }
    )

    return (
        f"Dashboard refreshed "
        f"for student {student_id}"
    )


# ==========================================================
# Lesson Completion Processing
# ==========================================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def process_lesson_completion(
    self,
    completion_id
):
    """
    Called whenever a lesson
    is marked complete.
    """

    from content_management.models import (
        LessonCompletion
    )

    # Query completion record and prefetch related student, module, chapter, and subject
    completion = (
        LessonCompletion.objects
        .select_related(
            "student",
            "module",
            "module__chapter",
            "module__chapter__subject"
        )
        .get(
            pk=completion_id
        )
    )

    # >>> ADDED / CHANGED: Wrap Celery dispatches in try-except block with synchronous fallback if worker dispatch fails
    try:
        refresh_student_dashboard_task.delay(
            str(completion.student_id)
        )
    except Exception as e:
        logger.warning("Celery dispatch failed for refresh_student_dashboard_task: %s", e)
        try:
            refresh_student_dashboard_task(str(completion.student_id))
        except Exception as inner_e:
            logger.error("Synchronous refresh_student_dashboard_task failed: %s", inner_e)

    # >>> ADDED / CHANGED: Trigger update of TeacherDashboard summary table for assigned teachers
    if completion.module and completion.module.chapter and completion.module.chapter.subject:
        try:
            from content_management.signals import get_teacher_ids_from_subject
            teacher_ids = get_teacher_ids_from_subject(completion.module.chapter.subject)
            for t_id in teacher_ids:
                t_id_str = str(t_id)
                try:
                    generate_teacher_module_analytics.delay(t_id_str)
                except Exception as e:
                    logger.warning("Celery dispatch failed for teacher analytics: %s", e)
                    try:
                        generate_teacher_module_analytics(t_id_str)
                    except Exception as inner_e:
                        logger.error("Synchronous teacher analytics failed: %s", inner_e)
        except Exception as e:
            logger.error("Failed updating teacher analytics on completion: %s", e)

    return (
        f"Processed completion "
        f"{completion_id}"
    )


# ==========================================================
# Module Completion Statistics
# ==========================================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def generate_module_completion_stats(
    self,
    module_id
):
    """
    Generates module analytics.

    Useful for:

    - teacher dashboard
    - admin dashboard
    - reporting
    """

    from content_management.models import (
        Module,
        LessonCompletion
    )

    module = (
        Module.objects
        .get(pk=module_id)
    )

    completion_count = (
        LessonCompletion.objects
        .filter(
            lesson__module=module,
            is_completed=True
        )
        .values(
            "student"
        )
        .distinct()
        .count()
    )

    return {
        "module_id":
            module.id,

        "module_title":
            module.title,

        "completed_students":
            completion_count,
    }


# ==========================================================
# Teacher Progress Analytics
# ==========================================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def generate_teacher_module_analytics(
    self,
    teacher_id
):
    """
    Analytics visible to teachers. Populates TeacherDashboard database table.
    """

    from users.models import User

    from content_management.models import (
        TeacherDashboard,
        LessonCompletion,
        ModuleProgress
    )

    teacher = (
        User.objects
        .get(pk=teacher_id)
    )

    chapters = (
        CacheService
        .get_teacher_chapters(
            teacher
        )
        .count()
    )

    modules_qs = (
        CacheService
        .get_teacher_modules(
            teacher
        )
    )

    modules_count = modules_qs.count()
    modules_published = modules_qs.filter(is_published=True).count()

    # >>> ADDED / CHANGED: Calculate total distinct students impacted across both completions and progress records
    completion_students = set(
        LessonCompletion.objects
        .filter(module__in=modules_qs)
        .values_list("student_id", flat=True)
    )
    progress_students = set(
        ModuleProgress.objects
        .filter(module__in=modules_qs)
        .values_list("student_id", flat=True)
    )
    students_impacted = len(completion_students | progress_students)

    # >>> ADDED / CHANGED: Update or create TeacherDashboard record with calculated analytics
    TeacherDashboard.objects.update_or_create(
        teacher=teacher,
        defaults={
            "modules_published": modules_published,
            "students_impacted": students_impacted,
            "average_completion_rate": 0
        }
    )

    return {
        "teacher_id": teacher.id,
        "chapters": chapters,
        "modules": modules_count,
        "modules_published": modules_published,
        "students_impacted": students_impacted,
    }


# ==========================================================
# Nightly Dashboard Aggregation & Backfill
# ==========================================================

# >>> ADDED: Celery task to backfill and refresh all student and teacher dashboards
@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def populate_all_dashboards_task(
    self
):
    """
    Backfills and refreshes StudentDashboard and TeacherDashboard tables
    for all active students and teachers in the system.
    """
    from users.models import User

    students = User.objects.filter(role="STUDENT")
    for s in students:
        try:
            refresh_student_dashboard_task.delay(str(s.id))
        except Exception as e:
            logger.error(f"Error refreshing dashboard for student {s.id}: {e}")

    teachers = User.objects.filter(role="TEACHER")
    for t in teachers:
        try:
            generate_teacher_module_analytics.delay(str(t.id))
        except Exception as e:
            logger.error(f"Error refreshing dashboard for teacher {t.id}: {e}")

    return f"Enqueued dashboard refresh for {students.count()} students and {teachers.count()} teachers."


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def aggregate_content_analytics(
    self
):
    """
    Nightly scheduled task.
    """

    from content_management.models import (
        Chapter,
        Module,
        LessonCompletion
    )

    analytics = {
        "chapters":
            Chapter.objects.count(),

        "modules":
            Module.objects.count(),

        "published_modules":
            Module.objects.filter(
                is_published=True
            ).count(),

        "lesson_completions":
            LessonCompletion.objects.filter(
                is_completed=True
            ).count()
    }

    return analytics