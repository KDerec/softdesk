from rest_framework import serializers
from .models import User
from .models import Project, Contributor, Issue, Comment


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
    author_user_id = serializers.ReadOnlyField(source="author_user.id")

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

    class Meta:
        model = Contributor
        fields = (
            "user_id",
            "project_id",
            "permission",
            "role",
        )
