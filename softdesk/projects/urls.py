from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"", views.ProjectViewSet, basename="project")

urlpatterns = router.urls
