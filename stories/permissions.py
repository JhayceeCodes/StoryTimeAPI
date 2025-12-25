from rest_framework.permissions import BasePermission



class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "author")
    

class IsStoryOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return hasattr(request.user, "author") and obj.author.user == request.user
    

class CanDeleteStory(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if hasattr(request.user, "author") and obj.author.user == request.user:
            return True

        if getattr(request.user, "role", None) in ("superuser", "admin", "moderator"):
            return True

        return False
        
