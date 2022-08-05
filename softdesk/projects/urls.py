from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()
router.register(r"", views.ProjectViewSet)

projects_router = routers.NestedSimpleRouter(router, r"", lookup="project")
projects_router.register(r"users", views.ContributorViewSet)
projects_router.register(r"issues", views.IssueViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(projects_router.urls)),
]
