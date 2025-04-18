from rest_framework import serializers
from .models import (
    Skill, Resume, ResumeSkill, Education, 
    Experience, ResumeAnalysis
)
from pydantic import BaseModel, ValidationError, Field
from typing import List, Dict, Optional
import re


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for the Skill model."""
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description']


class ResumeSkillSerializer(serializers.ModelSerializer):
    """Serializer for the ResumeSkill model (with skill details)."""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), 
        source='skill', 
        write_only=True
    )
    
    class Meta:
        model = ResumeSkill
        fields = ['id', 'skill', 'skill_id', 'confidence']


class EducationSerializer(serializers.ModelSerializer):
    """Serializer for the Education model."""
    class Meta:
        model = Education
        fields = ['id', 'institution', 'degree', 'field_of_study', 
                  'start_date', 'end_date', 'description']


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for the Experience model."""
    class Meta:
        model = Experience
        fields = ['id', 'company', 'position', 'location', 
                  'start_date', 'end_date', 'description']


class ResumeAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for the ResumeAnalysis model."""
    class Meta:
        model = ResumeAnalysis
        fields = ['id', 'overall_score', 'format_score', 'content_score', 
                  'skill_score', 'feedback', 'recommendations', 'analyzed_at']
        read_only_fields = ['analyzed_at']


class ResumeSerializer(serializers.ModelSerializer):
    """Serializer for the Resume model with related data."""
    skills = ResumeSkillSerializer(source='resumeskill_set', many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)
    analysis = ResumeAnalysisSerializer(read_only=True)
    
    class Meta:
        model = Resume
        fields = ['id', 'user', 'title', 'resume_file', 'file_type', 
                  'content_text', 'status', 'skills', 'education', 
                  'experience', 'analysis', 'created_at', 'updated_at']
        read_only_fields = ['content_text', 'status', 'created_at', 'updated_at']
    
    def validate_resume_file(self, value):
        """Validate that the uploaded file is a PDF or DOCX."""
        file_name = value.name.lower()
        if not (file_name.endswith('.pdf') or file_name.endswith('.docx')):
            raise serializers.ValidationError(
                "Only PDF and DOCX files are allowed."
            )
        return value
    
    def create(self, validated_data):
        """Create and return a new resume, triggering analysis."""
        # Set the file type based on the extension
        file_name = validated_data['resume_file'].name.lower()
        if file_name.endswith('.pdf'):
            validated_data['file_type'] = 'pdf'
        elif file_name.endswith('.docx'):
            validated_data['file_type'] = 'docx'
        
        resume = Resume.objects.create(**validated_data)
        
        # This would typically trigger a Celery task for async processing
        # from .tasks import process_resume
        # process_resume.delay(resume.id)
        
        return resume


class ResumeUploadSerializer(serializers.ModelSerializer):
    """Simplified serializer for resume upload only."""
    class Meta:
        model = Resume
        fields = ['title', 'resume_file']


# Pydantic models for validation
class EducationValidator(BaseModel):
    """Pydantic validator for education data."""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class ExperienceValidator(BaseModel):
    """Pydantic validator for experience data."""
    company: str
    position: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class SkillValidator(BaseModel):
    """Pydantic validator for skill data."""
    name: str
    confidence: float = Field(ge=0.0, le=1.0)


class ResumeDataValidator(BaseModel):
    """Pydantic validator for complete resume data extracted by AI."""
    skills: List[SkillValidator]
    education: List[EducationValidator]
    experience: List[ExperienceValidator]
    content_text: str


class ResumeAnalysisFeedbackValidator(BaseModel):
    """Pydantic validator for resume analysis feedback."""
    format_feedback: Dict[str, str]
    content_feedback: Dict[str, str]
    skill_feedback: Dict[str, str]
    recommendations: List[str]