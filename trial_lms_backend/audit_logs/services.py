from .models import AuditLog
# >>> CHANGED: Import SchoolUser model to resolve the school associated with the acting user
from schools.models import SchoolUser

def create_audit_log(
    *,
    user,
    action,
    object_type,
    object_id,
    metadata=None,
# >>> CHANGED: Added object_repr and content_type optional arguments for expanded audit logging metadata
    object_repr="",
    content_type=None,
    **kwargs
):
# >>> CHANGED: Safely resolve school_user relation and extract school instance
    school_user = SchoolUser.objects.filter(user=user).first()
    school = school_user.school if school_user else None

    meta = metadata or {}
    meta['object_type'] = object_type

# >>> CHANGED: Return newly created AuditLog instance with populated user, school, action, object_repr, and metadata
    return AuditLog.objects.create(
        user=user,
        school=school,
        action=action,
        content_type=content_type,
        object_id=str(object_id),
        object_repr=object_repr,
        metadata=meta,
    )