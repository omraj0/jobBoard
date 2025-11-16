from rest_framework.permissions import BasePermission

class CanManageJobs(BasePermission):
    """
    Custom permission to control access to the JobManagementViewSet.
    - View-level permission (has_permission):
      - Allows access to any authenticated 'is_staff' or 'is_superuser'.
      - Denies all 'normal' users.
    - Object-level permission (has_object_permission):
      - Superusers can do anything (GET, PUT, DELETE) to any object.
      - Staff users can only modify/delete objects they posted.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_staff or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.is_staff:
            return obj.posted_by == request.user
        return False