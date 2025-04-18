from django.db import models
from django.conf import settings


class Skill(models.Model):
    """Model to represent a skill that can be associated with a resume."""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'skills'


class Resume(models.Model):
    """Model to represent a user's resume."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending Analysis'),
        ('analyzed', 'Analysis Complete'),
        ('error', 'Analysis Error'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255)
    resume_file = models.FileField(upload_to='resumes/%Y/%m/%d/')
    file_type = models.CharField(max_length=10)  # pdf, docx
    content_text = models.TextField(blank=True)  # Extracted text content
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    skills = models.ManyToManyField(Skill, through='ResumeSkill')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s Resume - {self.title}"
    
    class Meta:
        db_table = 'resumes'


class ResumeSkill(models.Model):
    """Many-to-many relationship between Resume and Skill with confidence score."""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    confidence = models.FloatField(default=0.0)  # Confidence score of the skill detection
    
    class Meta:
        db_table = 'resume_skills'
        unique_together = ('resume', 'skill')


class Education(models.Model):
    """Model to represent education details extracted from a resume."""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"
    
    class Meta:
        db_table = 'education'


class Experience(models.Model):
    """Model to represent work experience details extracted from a resume."""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experience')
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.position} at {self.company}"
    
    class Meta:
        db_table = 'experience'


class ResumeAnalysis(models.Model):
    """Model to store AI analysis results for a resume."""
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='analysis')
    overall_score = models.FloatField(default=0.0)
    format_score = models.FloatField(default=0.0)
    content_score = models.FloatField(default=0.0)
    skill_score = models.FloatField(default=0.0)
    feedback = models.JSONField(default=dict)  # Stores structured feedback
    recommendations = models.JSONField(default=dict)  # Stores structured recommendations
    analyzed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resume_analysis'