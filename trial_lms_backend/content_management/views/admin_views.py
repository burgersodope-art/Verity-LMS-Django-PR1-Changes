# views/admin_views.py

from rest_framework import viewsets
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)

from common.audit_mixins import (
    AuditLogMixin
)

from django_filters.rest_framework import (
    DjangoFilterBackend
)

from common.permissions import IsAdmin

from content_management.models import (
    Chapter,
    Module,
    LessonContent
)

from content_management.serializers import (
    ChapterSerializer,
    ModuleSerializer,
    LessonContentSerializer
)

from content_management.filters import (
    ChapterFilter,
    ModuleFilter,
    LessonFilter
)

from content_management.pagination import (
    StandardResultsSetPagination
)
from audit_logs.services import create_audit_log

print("<!---- Initializing Admin ViewSet... ----!>")


class ChapterAdminViewSet(AuditLogMixin,viewsets.ModelViewSet):

    permission_classes = [IsAdmin]
    audit_module = "CONTENT_CHAPTER"
    serializer_class = ChapterSerializer

    pagination_class = (
        StandardResultsSetPagination
    )

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

    queryset = (
        Chapter.objects
        .select_related(
            "grade",
            "subject"
        )
    )

    ##Method to create chapter via serializer
    def perform_create(self,serializer):

        instance = serializer.save()

        ##Creating audit logs
        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 88-88)
            user=self.request.user,
            action="CREATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 90-90)
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
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 102-102)
            user=self.request.user,
            action="UPDATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 104-104)
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
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 117-117)
            user=self.request.user,
            action="UPDATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 119-119)
            object_type="CHAPTER",
            object_id=str(chapter.id)
        ) 
    ##Method to remove chapter with audit logs
    def perform_destroy(
        self,
        instance
    ):

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 129-129)
            user=self.request.user,
            action="DELETE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 131-131)
            object_type="CHAPTER",
            object_id=str(instance.id)
        )

        instance.delete()


class ModuleAdminViewSet(
    AuditLogMixin,
    viewsets.ModelViewSet
):
    audit_module = "CONTENT_MODULE"
    permission_classes = [IsAdmin]

    serializer_class = ModuleSerializer

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

    queryset = (
        Module.objects
        .select_related(
            "chapter"
        )
    )

    ##Method to create Module via serializer
    def perform_create(self,serializer):

        module = serializer.save()

        ##Creating audit logs
        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 182-182)
            user=self.request.user,
            action="CREATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 184-184)
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
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 196-196)
            user=self.request.user,
            action="UPDATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 198-198)
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
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 211-211)
            user=self.request.user,
            action="UPDATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 213-213)
            object_type="MODULE",
            object_id=str(module.id)
        ) 
    ##Method to remove chapter with audit logs
    def perform_destroy(
        self,
        instance
    ):

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 223-223)
            user=self.request.user,
            action="DELETE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 225-225)
            object_type="MODULE",
            object_id=str(instance.id)
        )

        instance.delete()


class LessonAdminViewSet(
    AuditLogMixin,
    viewsets.ModelViewSet
):

    permission_classes = [IsAdmin]

    serializer_class = (
        LessonContentSerializer
    )

    pagination_class = (
        StandardResultsSetPagination
    )

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = LessonFilter

    search_fields = [
        "title"
    ]

    ordering_fields = [
        "created_at"
    ]

    queryset = (
        LessonContent.objects
        .select_related(
            "module",
            "created_by"
        )
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
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 282-282)
            user=self.request.user,
            action="CREATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 284-284)
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
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 298-298)
            user=self.request.user,
            action="UPDATE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 300-300)
        object_type="LESSON",
            object_id=str(lesson.id)
        )

    ##Method to delete lesson with audit_logs
    def perform_destroy(
        self,
        instance
    ):

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 311-311)
            user=self.request.user,
            action="DELETE",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 313-313)
            object_type="LESSON",
            object_id=str(instance.id)
        )

        instance.delete()

print("<!---- Initialized Admin ViewSet!!! ----!>")