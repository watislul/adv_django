from celery import shared_task
from .models import Resume, Skill, ResumeSkill, Education, Experience, ResumeAnalysis
import nltk
import spacy
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize NLP models
# In a real app, we would download these models during the deployment
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # For development purposes
    nlp = None

# Define common skills for our domain
COMMON_SKILLS = [
    "Python", "Java", "JavaScript", "React", "Angular", "Vue", "Node.js",
    "Django", "Flask", "Spring", "Express", "SQL", "NoSQL", "MongoDB",
    "PostgreSQL", "MySQL", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
    "CI/CD", "Git", "REST API", "GraphQL", "HTML", "CSS", "Sass", "TensorFlow",
    "PyTorch", "Machine Learning", "Deep Learning", "Data Science", "NLP",
    "Computer Vision", "Agile", "Scrum", "Product Management", "UI/UX",
    "C++", "C#", "Ruby", "PHP", ".NET", "Swift", "Kotlin", "Go"
]


@shared_task
def process_resume(resume_id):
    """
    Process a resume to extract information using NLP.
    This is a background task that runs asynchronously.
    """
    try:
        resume = Resume.objects.get(id=resume_id)
        
        # Skip if already processed
        if resume.status == 'analyzed':
            return "Resume already analyzed"
        
        # Extract text from the resume file
        # In a real app, we would use libraries like PyPDF2 or python-docx
        # Here we'll assume the text is already extracted
        if not resume.content_text:
            # For demo, using sample text if no content exists
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
            resume.save()
        
        text = resume.content_text
        
        # Extract information using NLP
        if nlp:
            # Process the text with spaCy
            doc = nlp(text)
            
            # Extract skills
            extracted_skills = extract_skills(doc, text)
            for skill_name, confidence in extracted_skills:
                skill, created = Skill.objects.get_or_create(name=skill_name)
                ResumeSkill.objects.create(
                    resume=resume,
                    skill=skill,
                    confidence=confidence
                )
            
            # Extract education
            educations = extract_education(doc, text)
            for edu in educations:
                Education.objects.create(
                    resume=resume,
                    **edu
                )
            
            # Extract experience
            experiences = extract_experience(doc, text)
            for exp in experiences:
                Experience.objects.create(
                    resume=resume,
                    **exp
                )
            
            # Generate analysis
            analysis = analyze_resume(resume, doc, text)
            ResumeAnalysis.objects.create(
                resume=resume,
                **analysis
            )
        else:
            # Fallback if NLP models aren't available
            # Create sample data for demonstration
            
            # Extract skills
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
                start_date=datetime(2018, 1, 1),
                end_date=datetime(2022, 1, 1),
                description="Graduated with honors"
            )
            
            # Add experience
            Experience.objects.create(
                resume=resume,
                company="Google",
                position="Software Engineer",
                location="Mountain View, CA",
                start_date=datetime(2022, 1, 1),
                description="Developed and maintained web applications using React and Django."
            )
            
            Experience.objects.create(
                resume=resume,
                company="Microsoft",
                position="Intern",
                location="Redmond, WA",
                start_date=datetime(2021, 6, 1),
                end_date=datetime(2021, 8, 31),
                description="Worked on cloud infrastructure projects using Azure."
            )
            
            # Create analysis
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
        
        # Update resume status
        resume.status = 'analyzed'
        resume.save()
        
        return f"Successfully processed resume {resume_id}"
    
    except Resume.DoesNotExist:
        logger.error(f"Resume with ID {resume_id} not found")
        return f"Resume with ID {resume_id} not found"
    
    except Exception as e:
        logger.error(f"Error processing resume {resume_id}: {str(e)}")
        # Update status to error
        try:
            resume = Resume.objects.get(id=resume_id)
            resume.status = 'error'
            resume.save()
        except:
            pass
        return f"Error processing resume: {str(e)}"


def extract_skills(doc, text):
    """Extract skills from the document using NLP."""
    # In a real app, this would be a more sophisticated algorithm
    skills = []
    
    # Simple pattern matching for common skills
    for skill in COMMON_SKILLS:
        pattern = re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE)
        if pattern.search(text):
            # Confidence is higher for exact matches
            confidence = 0.9 if any(token.text == skill for token in doc) else 0.7
            skills.append((skill, confidence))
    
    return skills


def extract_education(doc, text):
    """Extract education information from the document."""
    # This would be a more sophisticated parser in a real app
    # For demo, return sample data
    return [
        {
            'institution': 'Stanford University',
            'degree': 'Bachelor of Science',
            'field_of_study': 'Computer Science',
            'start_date': datetime(2018, 1, 1),
            'end_date': datetime(2022, 1, 1),
            'description': 'Graduated with honors'
        }
    ]


def extract_experience(doc, text):
    """Extract work experience information from the document."""
    # This would be a more sophisticated parser in a real app
    # For demo, return sample data
    return [
        {
            'company': 'Google',
            'position': 'Software Engineer',
            'location': 'Mountain View, CA',
            'start_date': datetime(2022, 1, 1),
            'description': 'Developed and maintained web applications using React and Django.'
        },
        {
            'company': 'Microsoft',
            'position': 'Intern',
            'location': 'Redmond, WA',
            'start_date': datetime(2021, 6, 1),
            'end_date': datetime(2021, 8, 31),
            'description': 'Worked on cloud infrastructure projects using Azure.'
        }
    ]


def analyze_resume(resume, doc, text):
    """Generate analysis and recommendations for a resume."""
    # This would be a more sophisticated analyzer in a real app
    # For demo, return sample data
    return {
        'overall_score': 0.85,
        'format_score': 0.90,
        'content_score': 0.80,
        'skill_score': 0.85,
        'feedback': {
            'format': 'Good structure and formatting.',
            'content': 'Strong experience section, but consider adding more achievements.',
            'skills': 'Good technical skills, but missing soft skills.'
        },
        'recommendations': {
            'skills_to_add': ['Communication', 'Teamwork', 'Problem-solving'],
            'format_improvements': ['Add a professional summary', 'Use bullet points for achievements'],
            'content_improvements': ['Quantify achievements', 'Add more details about projects']
        }
    }