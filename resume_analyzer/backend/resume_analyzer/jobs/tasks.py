from celery import shared_task
from .models import Job, JobMatch
from resumes.models import Resume
import logging

logger = logging.getLogger(__name__)


@shared_task
def match_job_with_resumes(job_id):
    """
    Match a job with all available resumes and calculate compatibility scores.
    This is a background task that runs asynchronously.
    """
    try:
        job = Job.objects.get(id=job_id)
        
        # Get job skills
        job_skills = list(job.skills.all().values_list('id', flat=True))
        
        # Find resumes with potentially matching skills
        matching_resumes = Resume.objects.filter(
            skills__in=job_skills,
            status='analyzed'  # Only consider analyzed resumes
        ).distinct()
        
        # Calculate compatibility scores
        for resume in matching_resumes:
            # Calculate skill match percentage
            resume_skills = list(resume.skills.all().values_list('id', flat=True))
            common_skills = set(job_skills).intersection(resume_skills)
            skill_match_percentage = len(common_skills) / len(job_skills) if job_skills else 0
            
            # Calculate experience match (simplified)
            experience_match_score = calculate_experience_match(job, resume)
            
            # Check location match
            location_match = is_location_match(job.location, resume.user.profile.location)
            
            # Overall compatibility score
            compatibility_score = (
                (skill_match_percentage * 0.6) + 
                (experience_match_score * 0.3) + 
                (0.1 if location_match else 0)
            )
            
            # Create or update JobMatch
            JobMatch.objects.update_or_create(
                job=job,
                resume=resume,
                defaults={
                    'compatibility_score': compatibility_score,
                    'skill_match_percentage': skill_match_percentage,
                    'experience_match_score': experience_match_score,
                    'location_match': location_match
                }
            )
        
        return f"Successfully matched job {job_id} with {matching_resumes.count()} resumes"
    
    except Job.DoesNotExist:
        logger.error(f"Job with ID {job_id} not found")
        return f"Job with ID {job_id} not found"
    
    except Exception as e:
        logger.error(f"Error matching job {job_id}: {str(e)}")
        return f"Error matching job: {str(e)}"


@shared_task
def match_resume_with_jobs(resume_id):
    """
    Match a resume with all active jobs and calculate compatibility scores.
    This is a background task that runs asynchronously.
    """
    try:
        resume = Resume.objects.get(id=resume_id)
        
        # Only proceed if the resume has been analyzed
        if resume.status != 'analyzed':
            return f"Resume {resume_id} has not been analyzed yet"
        
        # Get resume skills
        resume_skills = list(resume.skills.all().values_list('id', flat=True))
        
        # Find active jobs with potentially matching skills
        matching_jobs = Job.objects.filter(
            status='active',
            skills__in=resume_skills
        ).distinct()
        
        # Calculate compatibility scores
        for job in matching_jobs:
            # Calculate skill match percentage
            job_skills = list(job.skills.all().values_list('id', flat=True))
            common_skills = set(resume_skills).intersection(job_skills)
            skill_match_percentage = len(common_skills) / len(job_skills) if job_skills else 0
            
            # Calculate experience match (simplified)
            experience_match_score = calculate_experience_match(job, resume)
            
            # Check location match
            location_match = is_location_match(job.location, resume.user.profile.location)
            
            # Overall compatibility score
            compatibility_score = (
                (skill_match_percentage * 0.6) + 
                (experience_match_score * 0.3) + 
                (0.1 if location_match else 0)
            )
            
            # Create or update JobMatch
            JobMatch.objects.update_or_create(
                job=job,
                resume=resume,
                defaults={
                    'compatibility_score': compatibility_score,
                    'skill_match_percentage': skill_match_percentage,
                    'experience_match_score': experience_match_score,
                    'location_match': location_match
                }
            )
        
        return f"Successfully matched resume {resume_id} with {matching_jobs.count()} jobs"
    
    except Resume.DoesNotExist:
        logger.error(f"Resume with ID {resume_id} not found")
        return f"Resume with ID {resume_id} not found"
    
    except Exception as e:
        logger.error(f"Error matching resume {resume_id}: {str(e)}")
        return f"Error matching resume: {str(e)}"


def calculate_experience_match(job, resume):
    """
    Calculate how well a resume's experience matches a job's requirements.
    This is a simplified implementation for demonstration purposes.
    """
    # In a real app, this would consider:
    # - Years of experience
    # - Relevance of previous roles
    # - Industry alignment
    # - Required seniority
    
    # For demo, return a simplified score
    experience_entries = resume.experience.all()
    
    # If no experience, give a low score
    if not experience_entries:
        return 0.2
    
    # Based on job's experience level, assign score
    if job.experience_level == 'entry':
        # Entry level jobs don't need much experience
        return 0.8
    
    elif job.experience_level == 'mid':
        # Mid-level: ideally 2-5 years
        total_experience = sum(
            (e.end_date - e.start_date).days / 365 if e.end_date else 2
            for e in experience_entries
        )
        return min(0.9, max(0.3, total_experience / 5))
    
    elif job.experience_level == 'senior':
        # Senior: ideally 5+ years
        total_experience = sum(
            (e.end_date - e.start_date).days / 365 if e.end_date else 3
            for e in experience_entries
        )
        return min(0.9, max(0.2, total_experience / 8))
    
    elif job.experience_level == 'executive':
        # Executive: ideally 10+ years
        total_experience = sum(
            (e.end_date - e.start_date).days / 365 if e.end_date else 5
            for e in experience_entries
        )
        return min(0.9, max(0.1, total_experience / 15))
    
    # Default
    return 0.5


def is_location_match(job_location, user_location):
    """
    Check if the job location matches the user's location.
    This is a simplified implementation for demonstration purposes.
    """
    # In a real app, this would use geocoding and distance calculations
    if not user_location:
        return False
    
    # Simple substring check
    job_location = job_location.lower()
    user_location = user_location.lower()
    
    return (
        job_location in user_location or 
        user_location in job_location or
        job_location.split(',')[0].strip() == user_location.split(',')[0].strip()
    )