from django.test import TestCase, Client
from django.urls import reverse
from .models import ModelAnalysis, CaseStudy, EducationalResource
import json

class DashboardViewsTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        
        # Create sample case study
        self.case_study = CaseStudy.objects.create(
            title="Facial Recognition Bias",
            category="bias",
            summary="This case study examines bias in facial recognition systems",
            detailed_description="A detailed examination of how facial recognition systems exhibit racial and gender bias...",
            key_lessons="Importance of diverse training data, regular bias audits, and transparency."
        )
        
        # Create sample educational resource
        self.resource = EducationalResource.objects.create(
            title="Understanding Fairness Metrics",
            resource_type="guide",
            description="A comprehensive guide to fairness metrics in AI",
            content="This guide explores various metrics for measuring and evaluating fairness in AI systems..."
        )
    
    def test_index_view(self):
        """Test the index view loads correctly"""
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index.html')
    
    def test_bias_detection_view(self):
        """Test the bias detection view loads correctly"""
        response = self.client.get(reverse('dashboard:bias_detection'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/bias_detection.html')
    
    def test_transparency_view(self):
        """Test the transparency view loads correctly"""
        response = self.client.get(reverse('dashboard:transparency'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/transparency.html')
    
    def test_education_view(self):
        """Test the education view loads correctly"""
        response = self.client.get(reverse('dashboard:education'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/education.html')
        self.assertContains(response, "Understanding Fairness Metrics")
    
    def test_case_studies_view(self):
        """Test the case studies view loads correctly"""
        response = self.client.get(reverse('dashboard:case_studies'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/case_studies.html')
        self.assertContains(response, "Facial Recognition Bias")
