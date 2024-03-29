"""
URL configuration of "projects" application.
"""
from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()
router.register(r"", views.ProjectViewSet)

projects_router = routers.NestedSimpleRouter(router, r"", lookup="project")
projects_router.register(r"users", views.ContributorViewSet)
projects_router.register(r"issues", views.IssueViewSet)

issues_router = routers.NestedSimpleRouter(
    projects_router, r"issues", lookup="issue"
)
issues_router.register(r"comments", views.CommentViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(projects_router.urls)),
    path(r"", include(issues_router.urls)),
]
