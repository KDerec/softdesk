"""
Custom permissions.
"""
from rest_framework import permissions
from .models import Comment, Contributor, Issue
from .checker import check_project_exist_in_db


class IsAuthor(permissions.BasePermission):
    """Custom permission to check if connected user is the object author."""

    message = "Il faut être l'auteur de cet objet pour effectuer cet action."

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if obj.author_user == request.user:
            return True
        return False


class IsContributor(permissions.BasePermission):
    """Custom permission to check if connected user is project contributor."""

    message = (
        "Il faut être un contributeur du projet pour effectuer cette action."
    )

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        project_id = None
        if view.basename == "project" and view.detail is False:
            return True
        if view.basename == "project" and view.detail is True:
            project_id = request.parser_context["kwargs"]["pk"]
        if view.basename != "project":
            project_id = request.parser_context["kwargs"]["project_pk"]
        check_project_exist_in_db(project_id)
        if project_id:
            try:
                if Contributor.objects.filter(
                    project_id=int(project_id), user_id=request.user.id
                ):
                    return True
            except Contributor.DoesNotExist:
                return False

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if type(obj) == Comment:
            issue_id = obj.issue_id
            issue = Issue.objects.get(id=issue_id)
            project_id = issue.project_id
        else:
            project_id = obj.project_id
        if Contributor.objects.filter(
            project_id=int(project_id), user_id=request.user.id
        ):
            return True

        return False


class IsResponsibleContributor(permissions.BasePermission):
    """
    Custom permission to check if connected user is responsible project contributor.
    """

    message = "Il faut être un contributeur de type responsable du projet pour effectuer cette action."

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        project_id = request.parser_context["kwargs"]["project_pk"]
        check_project_exist_in_db(project_id)
        try:
            if (
                Contributor.objects.get(
                    project_id=int(project_id), user_id=request.user.id
                ).permission
                == "Responsable"
            ):
                return True
        except Contributor.DoesNotExist:
            return False

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if (
            Contributor.objects.get(
                project_id=int(obj.project_id), user_id=request.user.id
            ).permission
            == "Responsable"
        ):
            return True

        return False
