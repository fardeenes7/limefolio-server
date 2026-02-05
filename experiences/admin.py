from django.contrib import admin
from experiences.models import Experience, Skill, SocialLink


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['position', 'company', 'site', 'type', 'is_current', 'is_published', 'start_date', 'order']
    list_filter = ['type', 'is_current', 'is_published', 'site']
    search_fields = ['position', 'company', 'description']
    ordering = ['-is_current', '-start_date', 'order']
    date_hierarchy = 'start_date'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'site', 'category', 'proficiency', 'is_featured', 'is_published', 'order']
    list_filter = ['category', 'proficiency', 'is_featured', 'is_published', 'site']
    search_fields = ['name', 'description']
    ordering = ['-is_featured', 'category', 'order', 'name']


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['platform', 'username', 'site', 'url', 'order']
    list_filter = ['platform', 'site']
    search_fields = ['username', 'url']
    ordering = ['site', 'order', 'platform']
