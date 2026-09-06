from audit_logs.services import (
    create_audit_log
)


class AuditLogMixin:

    audit_module = None

    def perform_create(
        self,
        serializer
    ):

        instance = serializer.save()

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 18-18)
            user=self.request.user,
            action="CREATE",
            module=self.audit_module,
            object_id=str(instance.pk),
            object_repr=str(instance)
        )

    def perform_update(
        self,
        serializer
    ):

        instance = serializer.save()

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 33-33)
            user=self.request.user,
            action="UPDATE",
            module=self.audit_module,
            object_id=str(instance.pk),
            object_repr=str(instance)
        )

    def perform_destroy(
        self,
        instance
    ):

        create_audit_log(
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 46-46)
            user=self.request.user,
            action="DELETE",
            module=self.audit_module,
            object_id=str(instance.pk),
            object_repr=str(instance)
        )

        instance.delete()