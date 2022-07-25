from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Project, User, Contributor, Issue, Comment
from .serializers import ProjectSerializer, UserSerializer, SignUpSerializer, ContributorSerializer


class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = ()


class UserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
