from rest_framework.permissions import BasePermission


class HasInstance(BasePermission):
    def has_permission(self, request, view):
        return request.user.instance is not None
