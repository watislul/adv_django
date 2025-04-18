from django.db import models
from django.conf import settings
from resumes.models import Skill


class JobCategory(models.Model):
    """Model to represent job categories."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'job_categories'
        verbose_name_plural = 'Job Categories'


class Company(models.Model):
    """Model to represent companies that post jobs."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'companies'
        verbose_name_plural = 'Companies'


class Job(models.Model):
    """Model to represent job listings."""
    
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    )
    
    EXPERIENCE_LEVEL_CHOICES = (
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive Level'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('filled', 'Filled'),
        ('expired', 'Expired'),
        ('draft', 'Draft'),
    )
    
    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')
    description = models.TextField()
    requirements = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='entry')
    location = models.CharField(max_length=255)
    remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    skills = models.ManyToManyField(Skill, through='JobSkill')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    class Meta:
        db_table = 'jobs'


class JobSkill(models.Model):
    """Many-to-many relationship between Job and Skill with importance level."""
    
    IMPORTANCE_CHOICES = (
        ('required', 'Required'),
        ('preferred', 'Preferred'),
        ('nice_to_have', 'Nice to Have'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    importance = models.CharField(max_length=20, choices=IMPORTANCE_CHOICES, default='preferred')
    
    class Meta:
        db_table = 'job_skills'
        unique_together = ('job', 'skill')


class JobApplication(models.Model):
    """Model to represent a job application."""
    
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('reviewing', 'Reviewing'),
        ('shortlisted', 'Shortlisted'),
        ('interviewed', 'Interviewed'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.SET_NULL, null=True, related_name='job_applications')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    compatibility_score = models.FloatField(default=0.0)  # AI-generated match score
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)  # Recruiter notes
    
    class Meta:
        db_table = 'job_applications'
        unique_together = ('job', 'applicant')  # Can only apply once per job
    
    def __str__(self):
        return f"{self.applicant.email} applied for {self.job.title}"


class JobMatch(models.Model):
    """Model to store job-resume compatibility analysis."""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='matches')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.CASCADE, related_name='job_matches')
    compatibility_score = models.FloatField(default=0.0)
    skill_match_percentage = models.FloatField(default=0.0)
    experience_match_score = models.FloatField(default=0.0)
    location_match = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'job_matches'
        unique_together = ('job', 'resume')  # Only one match analysis per job-resume pair
    
    def __str__(self):
        return f"Match: {self.resume.user.email} - {self.job.title} ({self.compatibility_score}%)"