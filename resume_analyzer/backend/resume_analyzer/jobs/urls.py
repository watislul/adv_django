from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobCategoryViewSet, CompanyViewSet, JobViewSet,
    JobApplicationViewSet, JobMatchViewSet
)

router = DefaultRouter()
router.register(r'categories', JobCategoryViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'applications', JobApplicationViewSet)
router.register(r'matches', JobMatchViewSet)
router.register(r'', JobViewSet)

urlpatterns = [
    path('', include(router.urls)),
]