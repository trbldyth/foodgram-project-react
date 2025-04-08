from rest_framework import permissions


class CustomIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request is not None and request.user.is_authenticated
