from rest_framework import permissions
from .models import Contributor


class IsAuthor(permissions.BasePermission):
    message = "Il faut être l'auteur de cet objet pour effectuer cet action."

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if obj.author_user == request.user:
            return True
        return False


class IsContributor(permissions.BasePermission):
    message = (
        "Il faut être contributeur du projet pour effectuer cette action."
    )

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.id in Contributor.objects.filter(
            project_id=int(obj.id)
        ).values_list("user_id", flat=True):
            return True

        return False
