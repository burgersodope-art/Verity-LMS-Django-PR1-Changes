from rest_framework import viewsets
# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 2-2)
from rest_framework.permissions import AllowAny

from .models import School
from .serializers import SchoolSerializer
from .permissions import IsAdminOnly


print("<!---- Initializing School Views... ----!>")
class SchoolViewSet(
    viewsets.ModelViewSet
):

    queryset = School.objects.all()

    serializer_class = (
        SchoolSerializer
    )

# >>> CHANGED in commit 47214f0 — Fix user authentication, add school assignment, and update gitignore (lines 20-23)
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminOnly()]

    search_fields = [
        "school_name",
        "school_code",
        "city",
        "state",
    ]

    filterset_fields = [
        "city",
        "district",
        "state",
        "is_active",
    ]

    ordering_fields = [
        "school_name",
        "created_at",
    ]
print("<!---- Initializing School Views!!! ----!>")