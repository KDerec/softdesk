"""
Provides serializers for objects of "projects" application.
"""
from rest_framework import serializers
from .models import User, Project, Contributor, Issue, Comment
from .checker import check_user_email_exist


class SignUpSerializer(serializers.ModelSerializer):
    """Sign up serializer."""

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        """Return new user instance object."""
        user = User.objects.create_user(
            validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """User object serializer."""

    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
        )


class ProjectSerializer(serializers.ModelSerializer):
    """Project object serializer."""

    author_user_id = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = (
            "project_id",
            "title",
            "description",
            "type",
            "author_user_id",
        )


class ContributorSerializer(serializers.ModelSerializer):
    """Contributor object serializer."""

    project_id = serializers.ReadOnlyField()
    user_id = serializers.ReadOnlyField()
    user = serializers.EmailField(write_only=True)

    def validate_user(self, value):
        """Return user object or raise validation error."""
        check_user_email_exist(value)
        project_id = self.context["request"].parser_context["kwargs"][
            "project_pk"
        ]
        user_id = User.objects.filter(email=value).get().id

        if self.context["request"].method == "POST":
            if Contributor.objects.filter(project_id=project_id).filter(
                user_id=user_id
            ):
                raise serializers.ValidationError(
                    "Cet utilisateur est déjà un contributeur du projet."
                )

        return User.objects.filter(email=value).get()

    class Meta:
        model = Contributor
        fields = (
            "user_id",
            "user",
            "project_id",
            "permission",
            "role",
        )


class ContributorAutoAssignUserSerializer(serializers.ModelSerializer):
    """Contributor with hidden user field object serializer."""

    user = serializers.HiddenField(default="")

    class Meta:
        model = Contributor
        fields = (
            "user_id",
            "user",
            "project_id",
            "permission",
            "role",
        )


class IssueSerializer(serializers.ModelSerializer):
    """Issue object serializer."""

    project_id = serializers.ReadOnlyField()
    author_user_id = serializers.ReadOnlyField()
    assignee_user_id = serializers.ReadOnlyField()
    assignee_user = serializers.EmailField(write_only=True)

    def validate_assignee_user(self, value):
        """Return user object or raise validation error."""
        check_user_email_exist(value)
        project_id = self.context["request"].parser_context["kwargs"][
            "project_pk"
        ]
        user_id = User.objects.filter(email=value).get().id

        if user_id not in Contributor.objects.filter(
            project_id=int(project_id)
        ).values_list("user_id", flat=True):
            raise serializers.ValidationError(
                "Cet utilisateur n'est pas un contributeur du projet."
            )

        return User.objects.filter(email=value).get()

    class Meta:
        model = Issue
        fields = (
            "id",
            "title",
            "desc",
            "tag",
            "priority",
            "status",
            "project_id",
            "author_user_id",
            "assignee_user",
            "assignee_user_id",
            "created_time",
        )


class CommentSerializer(serializers.ModelSerializer):
    """Comment object serializer."""

    author_user_id = serializers.ReadOnlyField()
    issue_id = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = (
            "comment_id",
            "description",
            "author_user_id",
            "issue_id",
            "created_time",
        )
