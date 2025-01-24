from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    UserViewSet,
    ProjectViewSet,
    CategoryViewSet,
    PriorityViewSet,
    TaskViewSet,
    index,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"priorities", PriorityViewSet)
router.register(r"tasks", TaskViewSet)

urlpatterns = [
    path("", index, name="index"),
    path("api/", include(router.urls)),
]
