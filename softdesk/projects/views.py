"""
Manage all the views of the "projects" application.
"""
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    SAFE_METHODS,
)
from django.shortcuts import get_object_or_404
from .models import Project, User, Contributor, Issue, Comment
from .permissions import IsAuthor, IsContributor, IsResponsibleContributor
from .serializers import (
    SignUpSerializer,
    UserSerializer,
    ProjectSerializer,
    ContributorSerializer,
    ContributorAutoAssignUserSerializer,
    IssueSerializer,
    CommentSerializer,
)
from .checker import (
    check_and_get_contributor_id,
    check_project_exist_in_db,
    check_issue_exist_in_db,
    check_comment_exist_in_db,
    check_project_is_issue_attribut,
    check_issue_is_comment_attribut,
)


class SignUp(generics.CreateAPIView):
    """Concrete view for creating a model instance of user object."""

    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [IsAdminUser]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """A viewset that provides actions for user object."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """A viewset that provides actions for project object."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsContributor]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method not in SAFE_METHODS:
            return [permission() for permission in [IsAuthor, IsAuthenticated]]

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """Get the list of items for this view."""
        if self.detail == True:
            project_id = self.kwargs["pk"]
            return super().get_queryset().filter(id=project_id)
        project_id_list = self.create_project_id_list_connected_user()
        return super().get_queryset().filter(id__in=project_id_list)

    def perform_create(self, serializer):
        """Create a model instance of project and author contributor."""
        serializer.save(author_user=self.request.user)
        author_contributor = Contributor(
            user=self.request.user,
            project_id=serializer.instance.id,
            permission="Responsable",
            role="Auteur",
        )
        author_contributor.save()

    def create_project_id_list_connected_user(self):
        """Return project id list of the connected user."""
        project_id_list = []
        connected_user_id = self.request.user.id
        for contributor in Contributor.objects.filter(
            user_id=connected_user_id
        ):
            project_id_list.append(contributor.project_id)

        return project_id_list


class ContributorViewSet(viewsets.ModelViewSet):
    """A viewset that provides actions for contributor object."""

    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsContributor]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method not in SAFE_METHODS:
            return [
                permission()
                for permission in [IsResponsibleContributor, IsAuthenticated]
            ]

        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        """Return the class to use for the serializer."""
        if self.action == "update":
            return ContributorAutoAssignUserSerializer
        return super().get_serializer_class()

    def get_object(self):
        """Returns the object the view is displaying."""
        queryset = self.filter_queryset(self.get_queryset())
        kwargs = {}
        user_id = self.kwargs["pk"]
        project_id = self.kwargs["project_pk"]
        contributor_id = check_and_get_contributor_id(project_id, user_id)
        kwargs["pk"] = contributor_id

        obj = get_object_or_404(queryset, **kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self):
        """Get the list of items for this view."""
        project_id = self.kwargs["project_pk"]
        return super().get_queryset().filter(project_id=project_id)

    def perform_create(self, serializer):
        """Create a model instance."""
        project_id = int(self.kwargs["project_pk"])
        project = Project.objects.get(id=project_id)
        serializer.save(project=project)

    def perform_update(self, serializer):
        """Update a model instance."""
        user_id = int(self.kwargs["pk"])
        user = User.objects.get(id=user_id)
        serializer.save(user=user)


class IssueViewSet(viewsets.ModelViewSet):
    """A viewset that provides actions for issue object."""

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsContributor]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method not in SAFE_METHODS:
            return [
                permission()
                for permission in [IsAuthor, IsAuthenticated, IsContributor]
            ]

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """Get the list of items for this view."""
        project_id = self.kwargs["project_pk"]
        if self.detail == True:
            issue_id = self.kwargs["pk"]
            check_issue_exist_in_db(issue_id)
            check_project_is_issue_attribut(project_id, issue_id)
        return super().get_queryset().filter(project_id=project_id)

    def perform_create(self, serializer):
        """Create a model instance."""
        project_id = int(self.kwargs["project_pk"])
        project = Project.objects.get(id=project_id)
        serializer.save(project=project, author_user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """A viewset that provides actions for comment object."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsContributor]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method not in SAFE_METHODS:
            return [
                permission()
                for permission in [IsAuthor, IsAuthenticated, IsContributor]
            ]

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """Get the list of items for this view."""
        project_id = self.kwargs["project_pk"]
        issue_id = self.kwargs["issue_pk"]
        check_issue_exist_in_db(issue_id)
        check_project_is_issue_attribut(project_id, issue_id)
        if self.detail == True:
            comment_id = self.kwargs["pk"]
            check_comment_exist_in_db(comment_id)
            check_issue_is_comment_attribut(issue_id, comment_id)
        return super().get_queryset().filter(issue_id=issue_id)

    def perform_create(self, serializer):
        """Create a model instance."""
        project_id = self.kwargs["project_pk"]
        check_project_exist_in_db(project_id)
        issue_id = self.kwargs["issue_pk"]
        check_issue_exist_in_db(issue_id)
        issue = Issue.objects.get(id=int(issue_id))
        serializer.save(issue=issue, author_user=self.request.user)
