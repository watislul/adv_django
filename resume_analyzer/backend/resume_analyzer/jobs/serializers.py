from rest_framework import serializers
from .models import (
    JobCategory, Company, Job, JobSkill, 
    JobApplication, JobMatch
)
from resumes.models import Skill
from resumes.serializers import SkillSerializer
from users.serializers import UserSerializer


class JobCategorySerializer(serializers.ModelSerializer):
    """Serializer for the JobCategory model."""
    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'description']


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for the Company model."""
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'website', 
                  'logo', 'location', 'industry', 'created_at']
        read_only_fields = ['created_at']


class JobSkillSerializer(serializers.ModelSerializer):
    """Serializer for JobSkill model (with skill details)."""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), 
        source='skill', 
        write_only=True
    )
    
    class Meta:
        model = JobSkill
        fields = ['id', 'skill', 'skill_id', 'importance']


class JobSerializer(serializers.ModelSerializer):
    """Serializer for the Job model with related data."""
    company = CompanySerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source='company',
        write_only=True
    )
    category = JobCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=JobCategory.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    skills = JobSkillSerializer(source='jobskill_set', many=True, read_only=True)
    posted_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'company_id', 'posted_by',
            'category', 'category_id', 'description', 'requirements',
            'job_type', 'experience_level', 'location', 'remote',
            'salary_min', 'salary_max', 'skills', 'status',
            'created_at', 'updated_at', 'expires_at'
        ]
        read_only_fields = ['posted_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create and return a new job."""
        # Add the current user as posted_by
        request = self.context.get('request')
        if request and request.user:
            validated_data['posted_by'] = request.user
            
        return super().create(validated_data)


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for the JobApplication model."""
    job = JobSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(),
        source='job',
        write_only=True
    )
    applicant = UserSerializer(read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_id', 'applicant', 'resume',
            'cover_letter', 'status', 'compatibility_score',
            'applied_at', 'updated_at', 'notes'
        ]
        read_only_fields = [
            'applicant', 'status', 'compatibility_score',
            'applied_at', 'updated_at', 'notes'
        ]
    
    def create(self, validated_data):
        """Create and return a new job application."""
        # Add the current user as applicant
        request = self.context.get('request')
        if request and request.user:
            validated_data['applicant'] = request.user
            
        # Check if the user already applied for this job
        job = validated_data.get('job')
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            raise serializers.ValidationError("You have already applied for this job.")
            
        return super().create(validated_data)


class JobMatchSerializer(serializers.ModelSerializer):
    """Serializer for the JobMatch model."""
    job = JobSerializer(read_only=True)
    resume_id = serializers.PrimaryKeyRelatedField(source='resume', read_only=True)
    
    class Meta:
        model = JobMatch
        fields = [
            'id', 'job', 'resume_id', 'compatibility_score',
            'skill_match_percentage', 'experience_match_score',
            'location_match', 'created_at'
        ]
        read_only_fields = ['created_at']


class RecruiterJobApplicationSerializer(serializers.ModelSerializer):
    """Extended serializer for recruiters viewing applications."""
    job = JobSerializer(read_only=True)
    applicant = UserSerializer(read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'applicant', 'resume',
            'cover_letter', 'status', 'compatibility_score',
            'applied_at', 'updated_at', 'notes'
        ]
        read_only_fields = [
            'job', 'applicant', 'resume', 'cover_letter',
            'compatibility_score', 'applied_at', 'updated_at'
        ]