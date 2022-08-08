from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import NotFound, PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Project, User, Contributor, Issue, Comment
from .serializers import (
    CommentSerializer,
    ContributorAutoAssignUserSerializer,
    IssueSerializer,
    ProjectSerializer,
    UserSerializer,
    SignUpSerializer,
    ContributorSerializer,
)


class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [IsAdminUser]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        project_id_list = create_project_id_list_connected_user(self)
        if self.detail == True:
            project_id = self.kwargs["pk"]
            check_project_exist_in_db(project_id)
            if check_connected_user_is_project_contributor(self, project_id):
                return super().get_queryset().filter(id__in=project_id_list)
        if self.detail == False:
            return super().get_queryset().filter(id__in=project_id_list)

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)
        author_contributor = Contributor(
            user=self.request.user,
            project_id=serializer.instance.id,
            permission="Responsable",
            role="Auteur",
        )
        author_contributor.save()


class ContributorViewSet(viewsets.ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer

    def get_serializer_class(self):
        if self.action == "update":
            return ContributorAutoAssignUserSerializer
        return super().get_serializer_class()

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

        user_id = filter_kwargs["pk"]
        project_id = self.kwargs["project_pk"]
        contributor_id = get_contributor_id(project_id, user_id)
        filter_kwargs["pk"] = contributor_id

        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self):
        project_id = self.kwargs["project_pk"]
        check_project_exist_in_db(project_id)
        if check_connected_user_is_project_contributor(self, project_id):
            if self.detail == True:
                user_id = self.kwargs["pk"]
                check_contributor_exist_in_db(user_id)
            return super().get_queryset().filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = int(self.kwargs["project_pk"])
        check_project_exist_in_db(project_id)
        project = Project.objects.filter(id=project_id).get()
        serializer.save(project=project)

    def perform_update(self, serializer):
        user_id = int(self.kwargs["pk"])
        user = User.objects.filter(id=user_id).get()
        serializer.save(user=user)


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def get_queryset(self):
        project_id = self.kwargs["project_pk"]
        check_project_exist_in_db(project_id)
        if check_connected_user_is_project_contributor(self, project_id):
            if self.detail == True:
                issue_id = self.kwargs["pk"]
                check_issue_exist_in_db(issue_id)
                check_project_is_issue_attribut(project_id, issue_id)
            return super().get_queryset().filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = int(self.kwargs["project_pk"])
        check_project_exist_in_db(project_id)
        project = Project.objects.filter(id=project_id).get()
        serializer.save(project=project, author_user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        project_id = self.kwargs["project_pk"]
        check_project_exist_in_db(project_id)
        if check_connected_user_is_project_contributor(self, project_id):
            issue_id = self.kwargs["issue_pk"]
            check_issue_exist_in_db(issue_id)
            check_project_is_issue_attribut(project_id, issue_id)
            if self.detail == True:
                comment_id = self.kwargs["pk"]
                check_comment_exist_in_db(comment_id)
                check_issue_is_comment_attribut(issue_id, comment_id)
            return super().get_queryset().filter(issue_id=issue_id)

    def perform_create(self, serializer):
        project_id = self.kwargs["project_pk"]
        check_project_exist_in_db(project_id)
        issue_id = int(self.kwargs["issue_pk"])
        check_issue_exist_in_db(issue_id)
        issue = Issue.objects.filter(id=issue_id).get()
        serializer.save(issue=issue, author_user=self.request.user)


def check_project_exist_in_db(project_id):
    try:
        project_id = int(project_id)
        if project_id not in Project.objects.values_list("id", flat=True):
            raise NotFound("Le numéro de projet indiqué n'existe pas.")
    except ValueError:
        raise NotFound("Le numéro de projet indiqué n'est pas un numéro.")


def check_contributor_exist_in_db(user_id):
    try:
        user_id = int(user_id)
        if user_id not in Contributor.objects.values_list(
            "user_id", flat=True
        ):
            raise NotFound("Le numéro de contributeur indiqué n'existe pas.")
    except ValueError:
        raise NotFound(
            "Le numéro de contributeur indiqué n'est pas un numéro."
        )


def check_issue_exist_in_db(issue_id):
    try:
        issue_id = int(issue_id)
        if issue_id not in Issue.objects.values_list("id", flat=True):
            raise NotFound("Le numéro de issue indiqué n'existe pas.")
    except ValueError:
        raise NotFound("Le numéro de issue indiqué n'est pas un numéro.")


def check_comment_exist_in_db(comment_id):
    try:
        comment_id = int(comment_id)
        if comment_id not in Comment.objects.values_list("id", flat=True):
            raise NotFound("Le numéro de commentaire indiqué n'existe pas.")
    except ValueError:
        raise NotFound("Le numéro de commentaire indiqué n'est pas un numéro.")


def check_project_is_issue_attribut(project_id, issue_id):
    project_id = int(project_id)
    issue_id = int(issue_id)
    if project_id != Issue.objects.filter(id=issue_id).get().project_id:
        raise NotFound(
            "Le numéro de issue indiqué n'existe pas pour ce projet."
        )


def get_contributor_id(project_id, user_id):
    project_id = int(project_id)
    user_id = int(user_id)
    try:
        return (
            Contributor.objects.filter(user_id=user_id)
            .filter(project_id=project_id)
            .get()
            .id
        )
    except Contributor.DoesNotExist:
        raise NotFound(
            "Le numéro de d'utilisateur indiqué n'existe pas pour ce projet."
        )


def check_issue_is_comment_attribut(issue_id, comment_id):
    issue_id = int(issue_id)
    comment_id = int(comment_id)
    if issue_id != Comment.objects.filter(id=comment_id).get().issue_id:
        raise NotFound(
            "Le numéro de commentaire indiqué n'existe pas pour cet issue."
        )


def check_connected_user_is_project_contributor(self, project_id):
    connected_user_id = self.request.user.id
    if connected_user_id in Contributor.objects.filter(
        project_id=int(project_id)
    ).values_list("user_id", flat=True):
        return True
    else:
        raise PermissionDenied(
            f"Seul les contributeurs de ce projet (#{project_id}) sont autorisés à effectuer cette action."
        )


def create_project_id_list_connected_user(self):
    project_id_list = []
    connected_user_id = self.request.user.id
    for contributor in Contributor.objects.filter(user_id=connected_user_id):
        project_id_list.append(contributor.project_id)

    return project_id_list
