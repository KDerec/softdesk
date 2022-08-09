"""
Provides checker functions for the "projects" application.
"""
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from .models import Project, Contributor, Issue, Comment, User


def check_and_get_contributor_id(project_id, user_id):
    """
    Return id contributor according to project and user id or raise exception.
    """
    try:
        project_id = int(project_id)
        user_id = int(user_id)
        return Contributor.objects.get(
            user_id=user_id, project_id=project_id
        ).id
    except Contributor.DoesNotExist:
        raise NotFound("Le contributeur indiqué n'existe pas pour ce projet.")
    except ValueError:
        raise NotFound(
            "Le numéro de contributeur indiqué n'est pas un numéro."
        )


def check_project_exist_in_db(project_id):
    """Raise exception if project object not found in database."""
    try:
        project_id = int(project_id)
        if project_id not in Project.objects.values_list("id", flat=True):
            raise NotFound("Le numéro de projet indiqué n'existe pas.")
    except ValueError:
        raise NotFound("Le numéro de projet indiqué n'est pas un numéro.")


def check_issue_exist_in_db(issue_id):
    """Raise exception if issue object not found in database."""
    try:
        issue_id = int(issue_id)
        if issue_id not in Issue.objects.values_list("id", flat=True):
            raise NotFound("Le numéro de problème indiqué n'existe pas.")
    except ValueError:
        raise NotFound("Le numéro de problème indiqué n'est pas un numéro.")


def check_comment_exist_in_db(comment_id):
    """Raise exception if comment object not found in database."""
    try:
        comment_id = int(comment_id)
        if comment_id not in Comment.objects.values_list("id", flat=True):
            raise NotFound("Le numéro de commentaire indiqué n'existe pas.")
    except ValueError:
        raise NotFound("Le numéro de commentaire indiqué n'est pas un numéro.")


def check_project_is_issue_attribut(project_id, issue_id):
    """Raise exception if project_id isn't an attribut of issue object."""
    project_id = int(project_id)
    issue_id = int(issue_id)
    if project_id != Issue.objects.get(id=issue_id).project_id:
        raise NotFound(
            "Le numéro de problème indiqué n'existe pas pour ce projet."
        )


def check_issue_is_comment_attribut(issue_id, comment_id):
    """Raise exception if issue_id isn't an attribut of comment object."""
    issue_id = int(issue_id)
    comment_id = int(comment_id)
    if issue_id != Comment.objects.get(id=comment_id).issue_id:
        raise NotFound(
            "Le numéro de commentaire indiqué n'existe pas pour cet issue."
        )


def check_user_email_exist(email):
    if not User.objects.filter(email=email):
        raise serializers.ValidationError(
            "Cet email d'utilisateur n'existe pas."
        )
