from rest_framework import serializers
from .models import User, Project, Contributor, Issue, Comment


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
            "password",
        )


class ProjectSerializer(serializers.ModelSerializer):
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
    project_id = serializers.ReadOnlyField()
    user_id = serializers.ReadOnlyField()
    user = serializers.EmailField(write_only=True)

    def validate_user(self, value):
        if not User.objects.filter(email=value):
            raise serializers.ValidationError("Cet email d'utilisteur n'existe pas.")

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


class IssueSerializer(serializers.ModelSerializer):
    project_id = serializers.ReadOnlyField()
    author_user_id = serializers.ReadOnlyField()
    assignee_user_id = serializers.ReadOnlyField()
    assignee_user = serializers.EmailField(write_only=True)

    def validate_assignee_user(self, value):
        if not User.objects.filter(email=value):
            raise serializers.ValidationError("Cet email d'utilisteur n'existe pas.")

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
