from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    #: If set to True the manager will be serialized into migrations and will
    #: thus be available in e.g. RunPython operations.
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["email"]

    @property
    def user_id(self):
        return self.pk

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.id}, {self.email}"


class Project(models.Model):
    """Project model."""

    PROJECT_TYPE_CHOICES = [
        ("Back-End", "Back-End"),
        ("Front-End", "Front-End"),
        ("iOs", "iOs"),
        ("Android", "Android"),
    ]

    title = models.CharField(max_length=128, help_text="Titre du projet.")
    description = models.CharField(
        max_length=2048, help_text="Description du projet."
    )
    type = models.CharField(
        max_length=9,
        choices=PROJECT_TYPE_CHOICES,
        help_text="Type du projet (back-end, front-end, iOS ou Android).",
    )
    author_user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.id}, {self.title}"

    @property
    def project_id(self):
        return self.pk


class Contributor(models.Model):
    """Contributor model."""

    PERMISSION_CHOICES = [
        ("Responsable", "Responsable"),
        ("Contributeur", "Contributeur"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    permission = models.CharField(
        max_length=12,
        choices=PERMISSION_CHOICES,
    )
    role = models.CharField(
        max_length=128, blank=True, help_text="Rôle du contributeur."
    )

    class Meta:
        unique_together = (
            "user",
            "project",
        )
        ordering = ["user_id"]

    def __str__(self):
        """String for representing the Model object."""
        return f"user: {self.user}, project: {self.project}"


class Issue(models.Model):
    """Issue model."""

    ISSUE_TAG = [
        ("BUG", "BUG"),
        ("AMÉLIORATION", "AMÉLIORATION"),
        ("TÂCHE", "TÂCHE"),
    ]
    ISSUE_PRIORITY = [
        ("FAIBLE", "FAIBLE"),
        ("MOYENNE", "MOYENNE"),
        ("ÉLEVÉE", "ÉLEVÉE"),
    ]
    ISSUE_STATUS = [
        ("À FAIRE", "À FAIRE"),
        ("EN COURS", "EN COURS"),
        ("TERMINÉ", "TERMINÉ"),
    ]

    title = models.CharField(max_length=128, help_text="Titre du problème.")
    desc = models.CharField(
        max_length=128, help_text="Description du problème."
    )
    tag = models.CharField(
        max_length=12,
        choices=ISSUE_TAG,
        help_text="Balise du problème (BUG, AMÉLIORATION ou TÂCHE).",
    )
    priority = models.CharField(
        max_length=7,
        choices=ISSUE_PRIORITY,
        help_text="Priorité du problème (FAIBLE, MOYENNE ou ÉLEVÉE).",
    )
    status = models.CharField(
        max_length=8,
        choices=ISSUE_STATUS,
        help_text="Statut du problème (À faire, En cours ou Terminé).",
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    author_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="Issue_author_user"
    )
    assignee_user = models.ForeignKey(
        User,
        default=author_user,
        on_delete=models.CASCADE,
        related_name="Issue_assignee_user",
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_time"]

    def __str__(self):
        """String for representing the Model object."""
        return f"issue: {self.id}, {self.title}; project: {self.project}"


class Comment(models.Model):
    """Comment model."""

    description = models.CharField(
        max_length=2048, help_text="Description du commentaire."
    )
    author_user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_time"]

    def __str__(self):
        """String for representing the Model object."""
        return f"comment: {self.id}; issue: {self.issue}"

    @property
    def comment_id(self):
        return self.pk
