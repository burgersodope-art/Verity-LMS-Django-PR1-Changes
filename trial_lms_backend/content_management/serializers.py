from rest_framework import serializers

from .models import (
    Chapter,
    Module,
    LessonContent,
    LessonCompletion,
    ModuleProgress
)

print("<!---- Initializing content_management Serializers... ----!>")

class ChapterSerializer(serializers.ModelSerializer):
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 14-15)
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    subject_name = serializers.CharField(source="subject.subject_name", read_only=True)

    class Meta:
        model = Chapter
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):

        subject = attrs.get("subject")
        grade = attrs.get("grade")

        if subject.grade_id != grade.id:
            raise serializers.ValidationError(
                "Subject must belong to selected grade."
            )

        return attrs
    
class ModuleSerializer(serializers.ModelSerializer):
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 39-46)
    grade = serializers.UUIDField(source="chapter.grade_id", read_only=True)
    subject = serializers.UUIDField(source="chapter.subject_id", read_only=True)
    grade_name = serializers.CharField(source="chapter.grade.description", read_only=True)
    subject_name = serializers.CharField(source="chapter.subject.subject_name", read_only=True)
    chapter_name = serializers.CharField(source="chapter.title", read_only=True)
    published_by_email = serializers.EmailField(source="published_by.email", read_only=True)
    published_by_first_name = serializers.CharField(source="published_by.first_name", read_only=True)
    published_by_last_name = serializers.CharField(source="published_by.last_name", read_only=True)

    class Meta:
        model = Module
        fields = "__all__"

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

class ModuleProgressSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = ModuleProgress

        fields = "__all__"

        read_only_fields = (
            "student",
        )

class LessonContentSerializer(
    serializers.ModelSerializer
):

    created_by_email = serializers.EmailField(
        source="created_by.email",
        read_only=True
    )
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 80-87)
    created_by_first_name = serializers.CharField(
        source="created_by.first_name",
        read_only=True
    )
    created_by_last_name = serializers.CharField(
        source="created_by.last_name",
        read_only=True
    )

    class Meta:
        model = LessonContent

        fields = (
            "id",
            "module",
            "title",
            "content",
            "extra_notes",
            "pdf_file",
            "created_by",
            "created_by_email",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 101-102)
            "created_by_first_name",
            "created_by_last_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
        )

# content_management/serializers.py

class LessonCompletionSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = LessonCompletion

        fields = (
            "id",
            "student",
            "module",

            "is_started",
            "is_completed",

            "progress_percentage",

            "started_at",
            "completed_at",

            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "student",
            "created_at",
            "updated_at",
        )

print("<!---- Initialized content_management Serializers !!!----!>")