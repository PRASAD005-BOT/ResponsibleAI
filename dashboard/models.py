from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """Extended user profile for AI Ethics Platform users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    organization = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    interests = models.TextField(blank=True, help_text="AI ethics interests, comma separated")
    created_at = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved"""
    instance.profile.save()

class UserActivity(models.Model):
    """Track user activity in the platform"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"

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
    
    SAMPLE_DATASET_TYPES = [
        ('', '-- Not Specified --'),
        ('hiring_dataset', 'Hiring Decision Dataset'),
        ('loan_approval', 'Loan Approval Dataset'),
        ('healthcare_decisions', 'Healthcare Treatment Dataset'),
        ('criminal_justice', 'Criminal Justice Dataset'),
        ('marketing_targeting', 'Marketing Targeting Dataset'),
        ('insurance_pricing', 'Insurance Pricing Dataset'),
        ('educational_assessment', 'Educational Assessment Dataset'),
        ('credit_scoring', 'Credit Scoring Dataset'),
        ('housing_allocation', 'Housing Allocation Dataset'),
        ('facial_recognition', 'Facial Recognition Dataset'),
        ('nlp_sentiment', 'NLP Sentiment Analysis Dataset'),
        ('recommendation_system', 'Recommendation System Dataset')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    dataset_description = models.TextField()
    sample_dataset_type = models.CharField(max_length=50, choices=SAMPLE_DATASET_TYPES, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Link to user if authenticated
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='model_analyses')
    
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
