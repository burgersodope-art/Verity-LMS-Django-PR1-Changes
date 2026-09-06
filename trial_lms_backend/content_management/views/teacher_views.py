# views/teacher_views.py

from rest_framework import viewsets
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)

from django_filters.rest_framework import (
    DjangoFilterBackend
)

from common.permissions import IsTeacher, IsAssignedTeacher

from ..models import (Chapter,Module,LessonContent)

from content_management.serializers import (
    ChapterSerializer,
    ModuleSerializer,
    LessonContentSerializer
)

from content_management.filters import (ChapterFilter,ModuleFilter)

from content_management.pagination import (StandardResultsSetPagination)

from content_management.services.content_service import (get_teacher_chapters,get_teacher_modules)

from audit_logs.services import (
    create_audit_log
)

print("<!---- Initialized content_management Teacher ViewSet... ----!>")

class TeacherChapterViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ChapterSerializer
    permission_classes = [IsTeacher, IsAssignedTeacher]
    pagination_class = (StandardResultsSetPagination)

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = ChapterFilter

    search_fields = [
        "title",
        "subject__subject_name"
    ]

    ordering_fields = [
        "chapter_number",
        "created_at"
    ]

    ordering = ["chapter_number"]

    def get_queryset(self):

        teacher = (self.request.user.teacher_profile)

        return get_teacher_chapters(teacher)
    
    ##Method to create chapter via serializer
    def perform_create(self,serializer):

        instance = serializer.save()

        ##Creating audit logs
        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 74-74)
            user=self.request.user,
            action="CREATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 76-76)
            object_type="CHAPTER",
            object_id=str(instance.id)
        )
    ##method to update chapter with audit_logs
    def perform_update(
        self,
        serializer
    ):

        chapter = serializer.save()

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 88-88)
            user=self.request.user,
            action="UPDATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 90-90)
            object_type="CHAPTER",
            object_id=str(chapter.id)
        )
        
    ##method to update chapter with audit logs
    def perform_update(
        self,
        serializer
    ):

        chapter = serializer.save()

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 103-103)
            user=self.request.user,
            action="UPDATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 105-105)
            object_type="CHAPTER",
            object_id=str(chapter.id)
        ) 
    ##Method to remove chapter with audit logs
    def perform_destroy(
        self,
        instance
    ):

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 115-115)
            user=self.request.user,
            action="DELETE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 117-117)
            object_type="CHAPTER",
            object_id=str(instance.id)
        )

        instance.delete()

class TeacherModuleViewSet(
    viewsets.ReadOnlyModelViewSet
):

    serializer_class = ModuleSerializer

    permission_classes = [IsTeacher, IsAssignedTeacher]

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

    ordering = ["module_number"]

    def get_queryset(self):

        teacher = (
            self.request.user.teacher_profile
        )

        return get_teacher_modules(
            teacher
        )
    
    ##Method to create Module via serializer
    def perform_create(self,serializer):

        module = serializer.save()

        ##Creating audit logs
        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 171-171)
            user=self.request.user,
            action="CREATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 173-173)
            object_type="MODULE",
            object_id=str(module.id)
        )
    ##method to update module with audit_logs
    def perform_update(
        self,
        serializer
    ):

        module = serializer.save()

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 185-185)
            user=self.request.user,
            action="UPDATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 187-187)
            object_type="MODULE",
            object_id=str(module.id)
        )
        
    ##method to update chapter with audit logs
    def perform_update(
        self,
        serializer
    ):

        module = serializer.save()

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 200-200)
            user=self.request.user,
            action="UPDATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 202-202)
            object_type="MODULE",
            object_id=str(module.id)
        ) 
    ##Method to remove chapter with audit logs
    def perform_destroy(
        self,
        instance
    ):

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 212-212)
            user=self.request.user,
            action="DELETE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 214-214)
            object_type="MODULE",
            object_id=str(instance.id)
        )

        instance.delete()

class TeacherLessonViewSet(
    viewsets.ModelViewSet
):

    serializer_class = (
        LessonContentSerializer
    )

    permission_classes = [
        IsTeacher,
        IsAssignedTeacher
    ]

    pagination_class = (
        StandardResultsSetPagination
    )

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    search_fields = [
        "title",
        "module__title",
        "module__chapter__title"
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "module__module_number"
    ]

    ordering = [
        "module__module_number"
    ]

    def get_queryset(self):

        teacher = (
            self.request.user.teacher_profile
        )

        return (
            LessonContent.objects
            .select_related(
                "module",
                "module__chapter",
                "module__chapter__subject",
                "created_by"
            )
            .filter(
                module__chapter__subject__teacher_assignments__teacher=teacher
            )
            .distinct()
        )

    ##Method to create lesson with audit_logs
    def perform_create(
        self,
        serializer
    ):

        lesson = serializer.save(
            created_by=self.request.user
        )

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 290-290)
            user=self.request.user,
            action="CREATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 292-292)
            object_type="LESSON",
            object_id=str(lesson.id),
            object_repr=lesson.title
        )

    ##Method to update lesson with audit_logs
    def perform_update(
        self,
        serializer
    ):

        lesson = serializer.save()

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 306-306)
            user=self.request.user,
            action="UPDATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 308-308)
        object_type="LESSON",
            object_id=str(lesson.id)
        )

    ##Method to delete lesson with audit_logs
    def perform_destroy(
        self,
        instance
    ):

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 319-319)
            user=self.request.user,
            action="DELETE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 321-321)
            object_type="LESSON",
            object_id=str(instance.id)
        )

        instance.delete()

print("<!---- Initialized content_management Teacher ViewSet!!! ----!>")