from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    SAFE_METHODS,
)
from rest_framework.exceptions import NotFound, PermissionDenied
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
        project_id_list = create_project_id_list_connected_user(self)
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
        """Get the list of items for this view."""
        project_id = self.kwargs["project_pk"]
        return super().get_queryset().filter(project_id=project_id)

    def perform_create(self, serializer):
        """Create a model instance."""
        project_id = int(self.kwargs["project_pk"])
        project = Project.objects.filter(id=project_id).get()
        serializer.save(project=project)

    def perform_update(self, serializer):
        """Update a model instance."""
        user_id = int(self.kwargs["pk"])
        user = User.objects.filter(id=user_id).get()
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
        project = Project.objects.filter(id=project_id).get()
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
        issue = Issue.objects.filter(id=int(issue_id)).get()
        serializer.save(issue=issue, author_user=self.request.user)


def check_project_exist_in_db(project_id):
    """Raise exception if project object not found in database."""
    try:
        project_id = int(project_id)
        if project_id not in Project.objects.values_list("id", flat=True):
            raise NotFound("Le numéro de projet indiqué n'existe pas.")
    except ValueError:
        raise NotFound("Le numéro de projet indiqué n'est pas un numéro.")


def check_issue_exist_in_db(issue_id):
    """Raise exception if issue object not found in database."""
    try:
        issue_id = int(issue_id)
        if issue_id not in Issue.objects.values_list("id", flat=True):
            raise NotFound("Le numéro de problème indiqué n'existe pas.")
    except ValueError:
        raise NotFound("Le numéro de problème indiqué n'est pas un numéro.")


def check_comment_exist_in_db(comment_id):
    """Raise exception if comment object not found in database."""
    try:
        comment_id = int(comment_id)
        if comment_id not in Comment.objects.values_list("id", flat=True):
            raise NotFound("Le numéro de commentaire indiqué n'existe pas.")
    except ValueError:
        raise NotFound("Le numéro de commentaire indiqué n'est pas un numéro.")


def check_project_is_issue_attribut(project_id, issue_id):
    """Raise exception if project_id isn't an attribut of issue object."""
    project_id = int(project_id)
    issue_id = int(issue_id)
    if project_id != Issue.objects.filter(id=issue_id).get().project_id:
        raise NotFound(
            "Le numéro de problème indiqué n'existe pas pour ce projet."
        )


def check_issue_is_comment_attribut(issue_id, comment_id):
    """Raise exception if issue_id isn't an attribut of comment object."""
    issue_id = int(issue_id)
    comment_id = int(comment_id)
    if issue_id != Comment.objects.filter(id=comment_id).get().issue_id:
        raise NotFound(
            "Le numéro de commentaire indiqué n'existe pas pour cet issue."
        )


def get_contributor_id(project_id, user_id):
    """
    Return id contributor according to project and user id or raise exception.
    """
    try:
        project_id = int(project_id)
        user_id = int(user_id)
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
    except ValueError:
        raise NotFound(
            "Le numéro de contributeur indiqué n'est pas un numéro."
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
    """Return project id list of the connected user."""
    project_id_list = []
    connected_user_id = self.request.user.id
    for contributor in Contributor.objects.filter(user_id=connected_user_id):
        project_id_list.append(contributor.project_id)

    return project_id_list
