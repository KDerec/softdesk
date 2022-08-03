from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Project, User, Contributor, Issue, Comment
from .serializers import (
    ProjectSerializer,
    UserSerializer,
    SignUpSerializer,
    ContributorSerializer,
)


class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = ()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)


class ContributorViewSet(viewsets.ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        project_id = int(self.kwargs["project_pk"])
        serializer.save(project_id=project_id)
