from django.contrib import admin
from .models import (
    JobCategory, Company, Job, JobSkill, 
    JobApplication, JobMatch
)


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 0


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'industry', 'created_at')
    list_filter = ('industry', 'created_at')
    search_fields = ('name', 'description', 'location')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'experience_level', 'location', 'remote', 'status', 'created_at')
    list_filter = ('job_type', 'experience_level', 'remote', 'status', 'created_at')
    search_fields = ('title', 'company__name', 'description', 'requirements', 'location')
    inlines = [JobSkillInline]
    

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'compatibility_score', 'applied_at', 'updated_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('job__title', 'applicant__email', 'notes')


@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ('job', 'resume', 'compatibility_score', 'skill_match_percentage', 'location_match', 'created_at')
    list_filter = ('location_match', 'created_at')
    search_fields = ('job__title', 'resume__user__email')
    ordering = ('-compatibility_score',)