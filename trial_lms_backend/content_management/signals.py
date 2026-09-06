import logging

from django.db import transaction

from django.db.models.signals import (
    post_save,
    post_delete
)

from django.dispatch import receiver

from .models import (
    Chapter,
    Module,
    LessonContent
)

from content_management.tasks import (
    refresh_teacher_content_cache_task,
    generate_teacher_module_analytics
)

logger = logging.getLogger(__name__)


# ==========================================================
# Helper Function
# ==========================================================

def get_teacher_ids_from_subject(
    subject
):
    """
    Return unique teacher User IDs assigned
    to a subject.
    """

    return list(
        subject.teacher_assignments
        .values_list(
            # >>> CHANGED: Query teacher__user_id instead of teacher__id to fetch User UUID for Celery cache key
            "teacher__user_id",
            flat=True
        )
        .distinct()
    )


# >>> ADDED: Helper function to trigger recalculation of StudentDashboard metrics for enrolled students
def refresh_enrolled_students_dashboards(
    subject
):
    """
    Refresh StudentDashboard metrics for all students
    enrolled in a subject when lessons or modules change.
    """
    from academics.models import StudentSubjectEnrollment
    from content_management.tasks import refresh_student_dashboard_task

    student_user_ids = list(
        StudentSubjectEnrollment.objects
        .filter(subject=subject)
        .values_list("student__user_id", flat=True)
        .distinct()
    )

    def enqueue_students():
        for student_id in student_user_ids:
            student_id_str = str(student_id)
            try:
                refresh_student_dashboard_task.delay(student_id_str)
            except Exception as e:
                logger.warning("Celery dispatch failed for student dashboard refresh: %s", e)
                try:
                    refresh_student_dashboard_task(student_id_str)
                except Exception as inner_e:
                    logger.error("Synchronous student dashboard refresh failed: %s", inner_e)

    transaction.on_commit(enqueue_students)


def invalidate_teacher_cache(
    teacher_ids
):
    """
    Refresh teacher cache after
    successful database commit.

    Prevents workers from reading
    uncommitted data.
    """

    teacher_ids = list(
        set(filter(None, teacher_ids))
    )

    def enqueue():

        for teacher_id in teacher_ids:
            teacher_id_str = str(teacher_id)
            try:
                refresh_teacher_content_cache_task.delay(
                    teacher_id_str
                )
            except Exception as e:
                logger.warning("Celery dispatch failed for cache refresh: %s", e)
                try:
                    refresh_teacher_content_cache_task(teacher_id_str)
                except Exception as inner_e:
                    logger.error("Synchronous cache refresh failed: %s", inner_e)

            try:
                generate_teacher_module_analytics.delay(
                    teacher_id_str
                )
            except Exception as e:
                logger.warning("Celery dispatch failed for teacher analytics: %s", e)
                try:
                    generate_teacher_module_analytics(teacher_id_str)
                except Exception as inner_e:
                    logger.error("Synchronous teacher analytics failed: %s", inner_e)

    transaction.on_commit(
        enqueue
    )

# ==========================================================
# Module Signals
# ==========================================================

@receiver(post_save, sender=Module)
@receiver(post_delete, sender=Module)
def module_cache_handler(
    sender,
    instance,
    **kwargs
):
    """
    Triggered when module changes.

    Affects:
    - Teacher chapter list
    - Teacher module list
    - Enrolled student dashboards
    """

    teacher_ids = (
        get_teacher_ids_from_subject(
            instance.chapter.subject
        )
    )

    invalidate_teacher_cache(
        teacher_ids
    )

    # >>> ADDED: Trigger student dashboard refresh for enrolled students on module save/delete
    refresh_enrolled_students_dashboards(
        instance.chapter.subject
    )


# ==========================================================
# Chapter Signals
# ==========================================================

@receiver(post_save, sender=Chapter)
@receiver(post_delete, sender=Chapter)
def chapter_cache_handler(
    sender,
    instance,
    **kwargs
):
    """
    Triggered when chapter changes.
    """

    teacher_ids = (
        get_teacher_ids_from_subject(
            instance.subject
        )
    )

    invalidate_teacher_cache(
        teacher_ids
    )

    # >>> ADDED: Trigger student dashboard refresh for enrolled students on chapter save/delete
    refresh_enrolled_students_dashboards(
        instance.subject
    )


# ==========================================================
# Lesson Content Signals
# ==========================================================

@receiver(post_save, sender=LessonContent)
@receiver(post_delete, sender=LessonContent)
def lesson_content_cache_handler(
    sender,
    instance,
    **kwargs
):
    """
    Triggered when lesson content
    changes.
    """

    teacher_ids = (
        get_teacher_ids_from_subject(
            instance.module.chapter.subject
        )
    )

    invalidate_teacher_cache(
        teacher_ids
    )

    # >>> ADDED: Trigger student dashboard refresh for enrolled students on lesson content save/delete
    refresh_enrolled_students_dashboards(
        instance.module.chapter.subject
    )
