from rest_framework.permissions import BasePermission

class IsVerified(BasePermission):
    """
    Custom permission to allow only email-verified users.
    """
    def has_permission(self, request, view):
        return request.user.verified