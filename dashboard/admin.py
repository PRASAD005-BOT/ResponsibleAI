from django.contrib import admin
from .models import ModelAnalysis, CaseStudy, EducationalResource

# Register models for admin interface
admin.site.register(ModelAnalysis)
admin.site.register(CaseStudy)
admin.site.register(EducationalResource)
