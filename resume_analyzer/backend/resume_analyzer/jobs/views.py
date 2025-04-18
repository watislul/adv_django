from rest_framework import status, viewsets, generics, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    JobCategory, Company, Job, JobSkill, 
    JobApplication, JobMatch
)
from .serializers import (
    JobCategorySerializer, CompanySerializer, JobSerializer,
    JobSkillSerializer, JobApplicationSerializer, JobMatchSerializer,
    RecruiterJobApplicationSerializer
)
from resumes.models import Resume, Skill
from users.views import IsOwnerOrAdmin


class IsRecruiter(permissions.BasePermission):
    """Permission to check if user is a recruiter."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'recruiter'


class IsRecruiterOrReadOnly(permissions.BasePermission):
    """Permission to allow recruiters to create/edit or anyone to view."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'recruiter'


class IsJobPoster(permissions.BasePermission):
    """Permission to check if user posted the job."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.posted_by == request.user


class JobCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for job categories."""
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Use different permissions depending on the action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for companies."""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Use different permissions depending on the action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRecruiter()]
        return [permissions.IsAuthenticated()]


class JobViewSet(viewsets.ModelViewSet):
    """ViewSet for jobs."""
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsRecruiterOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_type', 'experience_level', 'remote', 'status']
    search_fields = ['title', 'description', 'requirements', 'location']
    ordering_fields = ['created_at', 'expires_at', 'title']
    
    def get_queryset(self):
        """Filter jobs by various parameters."""
        queryset = Job.objects.all()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__name=category)
        
        # Filter by skills (comma-separated list)
        skills = self.request.query_params.get('skills', None)
        if skills:
            skill_list = skills.split(',')
            for skill in skill_list:
                queryset = queryset.filter(skills__name__icontains=skill.strip())
        
        # Filter by company
        company = self.request.query_params.get('company', None)
        if company:
            queryset = queryset.filter(company__name__icontains=company)
        
        # Filter by salary range
        min_salary = self.request.query_params.get('min_salary', None)
        if min_salary:
            queryset = queryset.filter(salary_min__gte=min_salary)
        
        max_salary = self.request.query_params.get('max_salary', None)
        if max_salary:
            queryset = queryset.filter(salary_max__lte=max_salary)
        
        # Filter by poster (only for recruiters to see their own postings)
        if self.request.user.role == 'recruiter':
            posted_by_me = self.request.query_params.get('posted_by_me', None)
            if posted_by_me == 'true':
                queryset = queryset.filter(posted_by=self.request.user)
        
        # Default to showing only active jobs
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        else:
            queryset = queryset.filter(status='active')
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the posted_by field to the current user."""
        serializer.save(posted_by=self.request.user)
    
    def get_permissions(self):
        """Add IsJobPoster permission for update/delete."""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsRecruiter(), IsJobPoster()]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def add_skill(self, request, pk=None):
        """Add a skill to a job."""
        job = self.get_object()
        
        if job.posted_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only add skills to your own job postings.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        skill_id = request.data.get('skill_id')
        importance = request.data.get('importance', 'preferred')
        
        if not skill_id:
            return Response(
                {'error': 'Skill ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            skill = Skill.objects.get(id=skill_id)
        except Skill.DoesNotExist:
            return Response(
                {'error': 'Skill not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the skill is already added
        if JobSkill.objects.filter(job=job, skill=skill).exists():
            return Response(
                {'error': 'This skill is already added to the job.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add the skill
        job_skill = JobSkill.objects.create(
            job=job,
            skill=skill,
            importance=importance
        )
        
        return Response(
            JobSkillSerializer(job_skill).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def remove_skill(self, request, pk=None):
        """Remove a skill from a job."""
        job = self.get_object()
        
        if job.posted_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only remove skills from your own job postings.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        skill_id = request.data.get('skill_id')
        
        if not skill_id:
            return Response(
                {'error': 'Skill ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            job_skill = JobSkill.objects.get(job=job, skill_id=skill_id)
        except JobSkill.DoesNotExist:
            return Response(
                {'error': 'This skill is not associated with the job.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Remove the skill
        job_skill.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def match_resumes(self, request, pk=None):
        """Match resumes to this job."""
        job = self.get_object()
        
        # Only the job poster or admin can see matches
        if job.posted_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only see matches for your own job postings.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Find matching resumes
        # In a real app, this would be a more sophisticated algorithm
        # For now, we'll just match based on skills
        job_skills = list(job.skills.all().values_list('id', flat=True))
        
        # Find resumes with the same skills
        matching_resumes = Resume.objects.filter(
            skills__in=job_skills
        ).distinct()
        
        # Calculate compatibility score for each resume
        matches = []
        for resume in matching_resumes:
            # Calculate skill match percentage
            resume_skills = list(resume.skills.all().values_list('id', flat=True))
            common_skills = set(job_skills).intersection(resume_skills)
            skill_match_percentage = len(common_skills) / len(job_skills) if job_skills else 0
            
            # Calculate experience match (simplified)
            experience_match_score = 0.5  # Default to average
            
            # Check location match
            location_match = job.location.lower() in resume.user.profile.location.lower() if resume.user.profile.location else False
            
            # Overall compatibility score
            compatibility_score = (skill_match_percentage * 0.6) + (experience_match_score * 0.3) + (0.1 if location_match else 0)
            
            # Create or update JobMatch
            job_match, created = JobMatch.objects.update_or_create(
                job=job,
                resume=resume,
                defaults={
                    'compatibility_score': compatibility_score,
                    'skill_match_percentage': skill_match_percentage,
                    'experience_match_score': experience_match_score,
                    'location_match': location_match
                }
            )
            
            matches.append(job_match)
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x.compatibility_score, reverse=True)
        
        return Response(
            JobMatchSerializer(matches, many=True).data
        )


class JobApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for job applications."""
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter applications based on user role."""
        user = self.request.user
        
        # Admin can see all applications
        if user.is_staff:
            return JobApplication.objects.all()
        
        # Recruiters can see applications for their posted jobs
        if user.role == 'recruiter':
            return JobApplication.objects.filter(job__posted_by=user)
        
        # Job seekers can only see their own applications
        return JobApplication.objects.filter(applicant=user)
    
    def get_serializer_class(self):
        """Use different serializers for different users."""
        if self.request.user.role == 'recruiter':
            return RecruiterJobApplicationSerializer
        return JobApplicationSerializer
    
    def perform_create(self, serializer):
        """Set the applicant to the current user."""
        serializer.save(applicant=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update the status of an application (recruiter only)."""
        application = self.get_object()
        
        # Check if user is the job poster
        if application.job.posted_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only update status for applications to your own job postings.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        status_value = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not status_value:
            return Response(
                {'error': 'Status is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the application
        application.status = status_value
        application.notes = notes
        application.save()
        
        return Response(
            RecruiterJobApplicationSerializer(application).data
        )
    
    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """Get the current user's applications."""
        applications = JobApplication.objects.filter(applicant=request.user)
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)


class JobMatchViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing job matches (read-only)."""
    queryset = JobMatch.objects.all()
    serializer_class = JobMatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter matches based on user role."""
        user = self.request.user
        
        # Admin can see all matches
        if user.is_staff:
            return JobMatch.objects.all()
        
        # Recruiters can see matches for their posted jobs
        if user.role == 'recruiter':
            return JobMatch.objects.filter(job__posted_by=user)
        
        # Job seekers can only see matches for their own resumes
        return JobMatch.objects.filter(resume__user=user)