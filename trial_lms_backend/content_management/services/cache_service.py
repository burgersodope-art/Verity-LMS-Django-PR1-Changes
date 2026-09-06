from django.core.cache import cache

from content_management.models import (
    Chapter,
    Module
)

CACHE_TIMEOUT = 60 * 5


class CacheService:

    @staticmethod
    def get_teacher_chapters(teacher):

        cache_key = (
            f"teacher_chapters_{teacher.id}"
        )

        data = cache.get(cache_key)

        if data:
            return data

# >>> ADDED / CHANGED: Extract TeacherProfile from User or TeacherProfile model instance to prevent ValueError ('Must be TeacherProfile instance')
        teacher_profile = getattr(teacher, "teacher_profile", teacher)

        data = (
            Chapter.objects
            .select_related(
                "grade",
                "subject"
            )
            .filter(
                subject__teacher_assignments__teacher=teacher_profile
            )
            .distinct()
        )

        cache.set(
            cache_key,
            data,
            CACHE_TIMEOUT
        )

        return data

    @staticmethod
    def get_teacher_modules(teacher):

        cache_key = (
            f"teacher_modules_{teacher.id}"
        )

        data = cache.get(cache_key)

        if data:
            return data

# >>> ADDED / CHANGED: Extract TeacherProfile from User or TeacherProfile model instance to prevent ValueError ('Must be TeacherProfile instance')
        teacher_profile = getattr(teacher, "teacher_profile", teacher)

        data = (
            Module.objects
            .select_related(
                "chapter",
                "chapter__subject"
            )
            .filter(
                chapter__subject__teacher_assignments__teacher=teacher_profile
            )
            .distinct()
        )

        cache.set(
            cache_key,
            data,
            CACHE_TIMEOUT
        )

        return data

    @staticmethod
    def clear_teacher_cache(teacher_id):

        cache.delete(
            f"teacher_chapters_{teacher_id}"
        )

        cache.delete(
            f"teacher_modules_{teacher_id}"
        )
