from rest_framework.permissions import BasePermission


class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or obj == request.user))

