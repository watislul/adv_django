from rest_framework import status, viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings
import nltk
import spacy
import re
from collections import Counter

from .models import (
    Skill, Resume, ResumeSkill, Education, 
    Experience, ResumeAnalysis
)
from .serializers import (
    SkillSerializer, ResumeSerializer, ResumeUploadSerializer,
    EducationSerializer, ExperienceSerializer, ResumeAnalysisSerializer,
    ResumeDataValidator
)
from users.views import IsOwnerOrAdmin


class IsResumeOwnerOrRecruiter(permissions.BasePermission):
    """
    Custom permission to allow resume owners or recruiters to view resumes.
    """
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_staff:
            return True
        
        # Owner has full access
        if obj.user == request.user:
            return True
        
        # Recruiters can only view (GET, HEAD, OPTIONS)
        if request.user.role == 'recruiter' and request.method in permissions.SAFE_METHODS:
            return True
        
        return False


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing and searching skills."""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter skills by search query."""
        queryset = Skill.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class ResumeViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on resumes."""
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated, IsResumeOwnerOrRecruiter]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter resumes based on user role."""
        user = self.request.user
        
        # Admin can see all resumes
        if user.is_staff:
            return Resume.objects.all()
        
        # Recruiters can see all resumes
        if user.role == 'recruiter':
            return Resume.objects.all()
        
        # Job seekers can only see their own resumes
        return Resume.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """Set the user when creating a resume."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Process the resume file and extract information.
        This would normally be done by a Celery task.
        """
        resume = self.get_object()
        
        # Check if resume is already processed
        if resume.status == 'analyzed':
            return Response(
                {'message': 'Resume already analyzed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # In a real app, this would be done by a Celery task
            # Here, we'll just simulate the processing
            
            # 1. Extract text from the resume file
            # This would use libraries like PyPDF2 for PDFs or python-docx for DOCX files
            # For demo, we'll use a sample text
            sample_text = """
            John Doe
            Software Engineer
            
            Education:
            - Bachelor of Science in Computer Science, Stanford University, 2018-2022
            
            Experience:
            - Software Engineer, Google, 2022-Present
              Developed and maintained web applications using React and Django.
              
            - Intern, Microsoft, Summer 2021
              Worked on cloud infrastructure projects using Azure.
            
            Skills:
            Python, Django, JavaScript, React, SQL, Git, Docker
            """
            
            resume.content_text = sample_text
            
            # 2. Extract skills, education, and experience
            # This would use NLP libraries like spaCy or NLTK
            # For demo, we'll create some sample data
            
            # Extract and add skills
            skill_names = ["Python", "Django", "JavaScript", "React", "SQL", "Git", "Docker"]
            for skill_name in skill_names:
                skill, created = Skill.objects.get_or_create(name=skill_name)
                ResumeSkill.objects.create(
                    resume=resume,
                    skill=skill,
                    confidence=0.9
                )
            
            # Add education
            Education.objects.create(
                resume=resume,
                institution="Stanford University",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                start_date="2018-01-01",
                end_date="2022-01-01",
                description="Graduated with honors"
            )
            
            # Add experience
            Experience.objects.create(
                resume=resume,
                company="Google",
                position="Software Engineer",
                location="Mountain View, CA",
                start_date="2022-01-01",
                end_date=None,
                description="Developed and maintained web applications using React and Django."
            )
            
            Experience.objects.create(
                resume=resume,
                company="Microsoft",
                position="Intern",
                location="Redmond, WA",
                start_date="2021-06-01",
                end_date="2021-08-31",
                description="Worked on cloud infrastructure projects using Azure."
            )
            
            # 3. Create resume analysis
            ResumeAnalysis.objects.create(
                resume=resume,
                overall_score=0.85,
                format_score=0.90,
                content_score=0.80,
                skill_score=0.85,
                feedback={
                    "format": "Good structure and formatting.",
                    "content": "Strong experience section, but consider adding more achievements.",
                    "skills": "Good technical skills, but missing soft skills."
                },
                recommendations={
                    "skills_to_add": ["Communication", "Teamwork", "Problem-solving"],
                    "format_improvements": ["Add a professional summary", "Use bullet points for achievements"],
                    "content_improvements": ["Quantify achievements", "Add more details about projects"]
                }
            )
            
            # 4. Update resume status
            resume.status = 'analyzed'
            resume.save()
            
            return Response({
                'message': 'Resume processed successfully',
                'data': ResumeSerializer(resume).data
            })
        
        except Exception as e:
            resume.status = 'error'
            resume.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def my_resumes(self, request):
        """Get the current user's resumes."""
        resumes = Resume.objects.filter(user=request.user)
        serializer = self.get_serializer(resumes, many=True)
        return Response(serializer.data)


class EducationViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on education entries."""
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """Filter education entries by resume and user."""
        resume_id = self.kwargs.get('resume_pk')
        if resume_id:
            resume = get_object_or_404(Resume, id=resume_id)
            if resume.user == self.request.user or self.request.user.is_staff:
                return Education.objects.filter(resume_id=resume_id)
        return Education.objects.none()
    
    def perform_create(self, serializer):
        """Set the resume when creating an education entry."""
        resume_id = self.kwargs.get('resume_pk')
        resume = get_object_or_404(Resume, id=resume_id)
        if resume.user != self.request.user and not self.request.user.is_staff:
            self.permission_denied(self.request)
        serializer.save(resume=resume)


class ExperienceViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on experience entries."""
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """Filter experience entries by resume and user."""
        resume_id = self.kwargs.get('resume_pk')
        if resume_id:
            resume = get_object_or_404(Resume, id=resume_id)
            if resume.user == self.request.user or self.request.user.is_staff:
                return Experience.objects.filter(resume_id=resume_id)
        return Experience.objects.none()
    
    def perform_create(self, serializer):
        """Set the resume when creating an experience entry."""
        resume_id = self.kwargs.get('resume_pk')
        resume = get_object_or_404(Resume, id=resume_id)
        if resume.user != self.request.user and not self.request.user.is_staff:
            self.permission_denied(self.request)
        serializer.save(resume=resume)


class ResumeAnalysisView(generics.RetrieveAPIView):
    """View for retrieving resume analysis."""
    queryset = ResumeAnalysis.objects.all()
    serializer_class = ResumeAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated, IsResumeOwnerOrRecruiter]
    
    def get_object(self):
        """Get the resume analysis for the given resume."""
        resume_id = self.kwargs.get('resume_pk')
        resume = get_object_or_404(Resume, id=resume_id)
        self.check_object_permissions(self.request, resume)
        return get_object_or_404(ResumeAnalysis, resume=resume)