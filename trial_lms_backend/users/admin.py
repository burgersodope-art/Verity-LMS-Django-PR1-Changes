from django.contrib import admin
# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 2-3)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from schools.models import SchoolUser

# Register your models here.
from .models import User

# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 8-11)
class SchoolUserInline(admin.TabularInline):
    model = SchoolUser
    extra = 1
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 11-11)
    max_num = 1

# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 13-14)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [SchoolUserInline]

    list_display = (
        "email",
        "role",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 20-21)
        "phone_number",
        "is_verified",
        "is_active",
        "is_staff",
        "created_at",
    )

    search_fields = (
        "email",
        "username",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 30-31)
        "role",
        "phone_number",
    )

    list_filter = (
        "role",
        "is_verified",
        "is_active",
    )

# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 40-66)
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone_number")}),
        ("Permissions", {"fields": ("role", "is_verified", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "role",
                    "phone_number",
                    "is_verified",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )