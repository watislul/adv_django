from django.contrib import admin
from .models import (
    Skill, Resume, ResumeSkill, Education, 
    Experience, ResumeAnalysis
)


class ResumeSkillInline(admin.TabularInline):
    model = ResumeSkill
    extra = 0


class EducationInline(admin.StackedInline):
    model = Education
    extra = 0


class ExperienceInline(admin.StackedInline):
    model = Experience
    extra = 0


class AnalysisInline(admin.StackedInline):
    model = ResumeAnalysis
    can_delete = False
    max_num = 1


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'user__email')
    inlines = [ResumeSkillInline, EducationInline, ExperienceInline, AnalysisInline]
    readonly_fields = ('content_text',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category')


@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('resume', 'overall_score', 'analyzed_at')
    list_filter = ('analyzed_at',)
    search_fields = ('resume__title', 'resume__user__email')