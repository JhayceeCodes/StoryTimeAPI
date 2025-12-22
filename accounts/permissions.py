from rest_framework.permissions import BasePermission

class IsVerified(BasePermission):
    """
    Custom permission to allow only email-verified users.
    """
    message = "Please verify your email address to access this resource."
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_verified
        )