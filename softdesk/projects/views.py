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

    def get_queryset(self):
        id_projects_list = []
        id_connected_user = self.request.user.id
        for obj in Contributor.objects.filter(user_id=id_connected_user):
            id_projects_list.append(obj.project_id)
        return super().get_queryset().filter(id__in=id_projects_list)

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)
        author_contributor = Contributor(
            user_id=self.request.user.id,
            project_id=serializer.instance.id,
            permission="Responsable",
            role="Auteur",
        )
        author_contributor.save()


class ContributorViewSet(viewsets.ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        project_id = int(self.kwargs["project_pk"])
        serializer.save(project_id=project_id)
