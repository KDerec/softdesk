from rest_framework import serializers
from .models import Users


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ("id", "email", "password", "first_name", "last_name")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = Users.objects.create_user(
            validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"
