from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import ModelAnalysis, CaseStudy, EducationalResource, UserProfile, UserActivity

# Define inline admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

# Define custom User admin with profile
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_organization', 'get_date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__organization')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__organization')
    
    def get_organization(self, obj):
        return obj.profile.organization if hasattr(obj, 'profile') else ""
    get_organization.short_description = 'Organization'
    
    def get_date_joined(self, obj):
        return obj.date_joined
    get_date_joined.short_description = 'Date Joined'
    get_date_joined.admin_order_field = 'date_joined'

# Register the new UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# ModelAnalysis Admin
class ModelAnalysisAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'user', 'created_at')
    list_filter = ('model_type', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'model_type', 'dataset_description', 'user')
        }),
        ('Analysis Results', {
            'fields': ('bias_analysis', 'transparency_analysis', 'fairness_metrics'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

# CaseStudy Admin
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_date')
    list_filter = ('category', 'published_date')
    search_fields = ('title', 'summary', 'detailed_description')

# EducationalResource Admin
class EducationalResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'published_date')
    list_filter = ('resource_type', 'published_date')
    search_fields = ('title', 'description', 'content')

# UserActivity Admin
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'created_at', 'description')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'activity_type', 'description')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        # Prevent manual creation of activity records
        return False

# Register models for admin interface
admin.site.register(ModelAnalysis, ModelAnalysisAdmin)
admin.site.register(CaseStudy, CaseStudyAdmin)
admin.site.register(EducationalResource, EducationalResourceAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
