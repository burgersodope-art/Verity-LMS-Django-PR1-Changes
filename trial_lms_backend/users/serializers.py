from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 5-5)
from schools.models import School, SchoolUser
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only serializer used for:
    - Profile endpoint
    - User listing
    """

# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 16-30)
    school = serializers.SerializerMethodField()

    school_name = serializers.SerializerMethodField()
    
    def get_school(self, obj):
        school_user = obj.schooluser_set.first()
        if school_user:
            return school_user.school.id
        return None

    def get_school_name(self, obj):
        school_user = obj.schooluser_set.first()
        if school_user:
            return school_user.school.school_name
        return None

    class Meta:
        model = User

        fields = [
            "id",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 37-38)
            "first_name",
            "last_name",
            "email",
            "username",
            "role",
            "phone_number",
            "is_verified",
            "school",
            "school_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "is_verified",
            "created_at",
            "updated_at",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """
    User Registration Serializer
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )

    confirm_password = serializers.CharField(
# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 70-75)
        write_only=True
    )
    
    school = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = User

        fields = [
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 83-84)
            "first_name",
            "last_name",
            "email",
            "username",
            "password",
            "confirm_password",
            "role",
            "phone_number",
# >>> CHANGED in commit 1f1057c — feat(content_management): auto-calculate reading time and trigger student dashboard updates on lesson completion (lines 91-91)
            "is_verified",
            "school",
        ]

    def validate_email(self, value):

        if User.objects.filter(
            email__iexact=value
        ).exists():

            raise serializers.ValidationError(
                "Email already registered."
            )

        return value.lower()

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:

            raise serializers.ValidationError(
                {
                    "confirm_password":
                    "Passwords do not match."
                }
            )

# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 118-118)
        return attrs

    def create(self, validated_data):

        validated_data.pop(
            "confirm_password", None
# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 124-127)
        )

        password = validated_data.pop(
            "password"
        )
        
        school = validated_data.pop(
            "school", None
        )
# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 133-138)

        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        if school:
            SchoolUser.objects.create(
                user=user,
                school=school
            )

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Update Profile Serializer
    """

    class Meta:
        model = User

        fields = [
            "username",
            "phone_number",
        ]