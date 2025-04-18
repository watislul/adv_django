from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    SkillViewSet, ResumeViewSet, EducationViewSet,
    ExperienceViewSet, ResumeAnalysisView
)

router = DefaultRouter()
router.register(r'skills', SkillViewSet)
router.register(r'', ResumeViewSet)

# Nested routes for resume-related resources
resume_router = routers.NestedSimpleRouter(router, r'', lookup='resume')
resume_router.register(r'education', EducationViewSet, basename='resume-education')
resume_router.register(r'experience', ExperienceViewSet, basename='resume-experience')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(resume_router.urls)),
    path('<int:resume_pk>/analysis/', ResumeAnalysisView.as_view(), name='resume-analysis'),
]