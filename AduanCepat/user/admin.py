from django.contrib import admin
from .models import UserProfile, Submission


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone', 'occupation', 'is_verified', 'trust_score']
    list_filter  = ['is_verified']
    search_fields = ['user__username', 'full_name', 'phone']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display  = ['id', 'title', 'user', 'category', 'priority', 'status', 'created_at']
    list_filter   = ['status', 'category', 'priority']
    search_fields = ['title', 'user__username', 'location_address']
    list_editable = ['status']
    ordering      = ['-created_at']
