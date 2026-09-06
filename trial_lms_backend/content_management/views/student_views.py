# content_management/views/student_views.py

from django.utils import timezone

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)

from django_filters.rest_framework import (
    DjangoFilterBackend
)

from common.permissions import (
    IsStudent
)

from audit_logs.services import (
    create_audit_log
)

from content_management.models import (
    Module,
    LessonContent,
    LessonCompletion,
    ModuleProgress
)

from content_management.tasks import (
    process_lesson_completion
)

from content_management.serializers import (
    ModuleSerializer,
    LessonContentSerializer,
    LessonCompletionSerializer,
    ModuleProgressSerializer
)

from content_management.filters import (
    ModuleFilter
)

from content_management.pagination import (
    StandardResultsSetPagination
)

print("<!---- Initializing content_management Student ViewSet... ----!>")

class StudentModuleViewSet(
    viewsets.ReadOnlyModelViewSet
):

    serializer_class = ModuleSerializer

    permission_classes = [
        IsStudent
    ]

    pagination_class = (
        StandardResultsSetPagination
    )

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = ModuleFilter

    search_fields = [
        "title"
    ]

    ordering_fields = [
        "module_number",
        "created_at"
    ]

    ordering = [
        "module_number"
    ]

    def get_queryset(self):

        student = (
            self.request.user.student_profile
        )

        return (
            Module.objects
            .select_related(
                "chapter",
                "chapter__subject"
            )
            .filter(
                chapter__subject__studentsubjectenrollment__student=student,
                is_published=True
            )
            .distinct()
        )

    def list(
        self,
        request,
        *args,
        **kwargs
    ):

        create_audit_log(
            user=request.user,
            action="VIEW",
            object_type="MODULE_LIST",
            object_id=""
        )

        return super().list(
            request,
            *args,
            **kwargs
        )

    def retrieve(
        self,
        request,
        *args,
        **kwargs
    ):

        module = self.get_object()

        ModuleProgress.objects.get_or_create(
            student=request.user,
            module=module,
            defaults={
                "last_accessed_at":
                    timezone.now()
            }
        )

        create_audit_log(
            user=request.user,
            action="START",
            object_type="MODULE",
            object_id=str(module.id)
        )

        return super().retrieve(
            request,
            *args,
            **kwargs
        )
    
class StudentLessonViewSet(
    viewsets.ReadOnlyModelViewSet
):

    serializer_class = (
        LessonContentSerializer
    )

    permission_classes = [
        IsStudent
    ]

    def get_queryset(self):

        student = (
            self.request.user.student_profile
        )

        return (
            LessonContent.objects
            .select_related(
                "module",
                "module__chapter"
            )
            .filter(
                module__is_published=True,
                module__chapter__subject__studentsubjectenrollment__student=student
            )
            .distinct()
        )

    def retrieve(
        self,
        request,
        *args,
        **kwargs
    ):

        lesson = self.get_object()

        progress, _ = (
            ModuleProgress.objects.get_or_create(
                student=request.user,
                module=lesson.module
            )
        )

        progress.lessons_viewed += 1

        progress.last_accessed_at = (
            timezone.now()
        )

        progress.save()

        create_audit_log(
            user=request.user,
            action="START",
            object_type="LESSON",
            object_id=str(lesson.id)
        )

        # >>> ADDED: Trigger background Celery tasks asynchronously upon opening lesson to immediately sync dashboards
        try:
            from content_management.tasks import refresh_student_dashboard_task, generate_teacher_module_analytics
            from content_management.signals import get_teacher_ids_from_subject

            refresh_student_dashboard_task.delay(str(request.user.id))

            if lesson.module and lesson.module.chapter and lesson.module.chapter.subject:
                teacher_user_ids = get_teacher_ids_from_subject(lesson.module.chapter.subject)
                for t_id in teacher_user_ids:
                    generate_teacher_module_analytics.delay(str(t_id))
        except Exception as e:
            print(f"<!---- Could not dispatch dashboard refresh task on retrieve: {e} ----!>")

        return super().retrieve(
            request,
            *args,
            **kwargs
        )
    
class LessonCompletionViewSet(
    viewsets.ModelViewSet
):

    serializer_class = (
        LessonCompletionSerializer
    )

    permission_classes = [
        IsStudent
    ]

    pagination_class = (
        StandardResultsSetPagination
    )

    def get_queryset(self):

        return (
            LessonCompletion.objects
            .select_related(
                "module"
            )
            .filter(
                student=self.request.user
            )
        )

    def perform_create(
        self,
        serializer
    ):

        completion = serializer.save(
            student=self.request.user,
            is_started=True,
            started_at=timezone.now()
        )

        create_audit_log(
            user=self.request.user,
            action="START",
            object_type="LESSON",
            object_id=str(
                completion.module.id
            )
        )
    
    @action(
        detail=True,
        methods=["post"]
    )
    def complete(
        self,
        request,
        pk=None
    ):

        completion = self.get_object()

        completion.is_completed = True

        completion.completed_at = (
            timezone.now()
        )

        completion.save()

        progress, _ = (
            ModuleProgress.objects.get_or_create(
                student=request.user,
                module=completion.module
            )
        )

        progress.progress_percentage = 100

        progress.is_completed = True

        now_time = timezone.now()
        progress.completed_at = now_time
        # >>> ADDED: Update last_accessed_at timestamp when module is completed
        progress.last_accessed_at = now_time

        # >>> ADDED: Calculate time spent reading the lesson (in minutes) if started_at timestamp exists
        if completion.started_at:
            delta = now_time - completion.started_at
            progress.time_spent_minutes = max(1, int(delta.total_seconds() // 60))

        progress.save()

        create_audit_log(
            user=request.user,
            action="COMPLETE",
            object_type="LESSON",
            object_id=str(
                completion.module.id
            )
        )

        # >>> ADDED / CHANGED: Dispatch background Celery task to recalculate StudentDashboard and TeacherDashboard analytics asynchronously
        try:
            process_lesson_completion.delay(str(completion.id))
        except Exception as e:
            print(f"<!---- Could not dispatch process_lesson_completion task: {e} ----!>")

        return Response({
            "message":
            "Lesson completed successfully"
        })
    
    @action(
        detail=True,
        methods=["post"]
    )
    def update_progress(
        self,
        request,
        pk=None
    ):

        completion = self.get_object()

        percentage = int(
            request.data.get(
                "progress_percentage",
                0
            )
        )

        progress, _ = (
            ModuleProgress.objects.get_or_create(
                student=request.user,
                module=completion.module
            )
        )

        progress.progress_percentage = percentage

        progress.last_accessed_at = (
            timezone.now()
        )

        progress.save()

        create_audit_log(
            user=request.user,
            action="UPDATE",
            object_type="MODULE_PROGRESS",
            object_id=str(progress.id)
        )

        return Response({
            "progress_percentage":
            progress.progress_percentage
        })
    
print("<!---- Initialized content_management Student ViewSet!!! ----!>")