from django.db import models
from django.utils import timezone

class ModelAnalysis(models.Model):
    """Model for storing AI model analysis results"""
    
    MODEL_TYPES = [
        ('classification', 'Classification'),
        ('regression', 'Regression'),
        ('clustering', 'Clustering'),
        ('nlp', 'Natural Language Processing'),
        ('computer_vision', 'Computer Vision'),
        ('other', 'Other')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    dataset_description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Analysis results stored as JSON
    bias_analysis = models.JSONField(null=True, blank=True)
    transparency_analysis = models.JSONField(null=True, blank=True)
    fairness_metrics = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class CaseStudy(models.Model):
    """Model for storing AI ethics case studies"""
    
    CATEGORIES = [
        ('bias', 'Algorithmic Bias'),
        ('transparency', 'Model Transparency'),
        ('privacy', 'Data Privacy'),
        ('governance', 'AI Governance'),
        ('impact', 'Societal Impact')
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    summary = models.TextField()
    detailed_description = models.TextField()
    key_lessons = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class EducationalResource(models.Model):
    """Model for storing educational resources on AI ethics"""
    
    RESOURCE_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('guide', 'Guide'),
        ('framework', 'Framework'),
        ('checklist', 'Checklist'),
        ('tool', 'Tool'),
        ('reference', 'Reference')
    ]
    
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField()
    content = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    
    # For external resources
    external_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.title
