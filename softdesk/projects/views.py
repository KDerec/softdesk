from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Project, User, Contributor, Issue, Comment
from .serializers import (
    IssueSerializer,
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
        project_id_list = create_project_id_list_connected_user(self)
        if self.detail == True:
            project_id = self.kwargs["pk"]
            check_project_exist_in_db(project_id)
            if project_id in project_id_list:
                return super().get_queryset().filter(id__in=project_id_list)
            else:
                raise PermissionDenied()
        if self.detail == False:
            return super().get_queryset().filter(id__in=project_id_list)

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

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        filtered_contributor = Contributor.objects.filter(
            project_id=self.kwargs["project_pk"]
        ).filter(user_id=filter_kwargs["pk"])
        try:
            filter_kwargs["pk"] = filtered_contributor.get().id
        except:
            raise Http404
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self):
        return super().get_queryset().filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project_id = int(self.kwargs["project_pk"])
        serializer.save(project_id=project_id)


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        project = Project.objects.filter(id=self.kwargs["project_pk"]).get()
        serializer.save(project=project, author_user=self.request.user)


def check_project_exist_in_db(project_id):
    if project_id not in Project.objects.values_list("id", flat=True):
        raise Http404

def create_project_id_list_connected_user(self):
    project_id_list = []
    connected_user_id = self.request.user.id
    for contributor in Contributor.objects.filter(user_id=connected_user_id):
        project_id_list.append(contributor.project_id)

    return project_id_list
