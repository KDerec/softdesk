from rest_framework import permissions
from rest_framework.exceptions import NotFound
from .models import Contributor, Project


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
        "Il faut être un contributeur du projet pour effectuer cette action."
    )

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        project_id = None
        if view.basename == "project" and view.detail == False:
            return True
        if view.basename == "project" and view.detail == True:
            project_id = request.parser_context["kwargs"]["pk"]
        if view.basename != "project":
            project_id = request.parser_context["kwargs"]["project_pk"]
        check_project_exist_in_db(project_id)
        if project_id:
            try:
                if request.user.id in Contributor.objects.filter(
                    project_id=int(project_id)
                ).values_list("user_id", flat=True):
                    return True
            except Contributor.DoesNotExist:
                return False

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.id in Contributor.objects.filter(
            project_id=int(obj.project_id)
        ).values_list("user_id", flat=True):
            return True

        return False



def check_project_exist_in_db(project_id):
    """Raise exception if project object not found in database."""
    try:
        project_id = int(project_id)
        if project_id not in Project.objects.values_list("id", flat=True):
            raise NotFound("Le numéro de projet indiqué n'existe pas.")
    except ValueError:
        raise NotFound("Le numéro de projet indiqué n'est pas un numéro.")
