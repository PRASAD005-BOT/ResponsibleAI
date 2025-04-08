from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
import pandas as pd
import numpy as np
import io

from .models import ModelAnalysis, CaseStudy, EducationalResource
from .forms import ModelUploadForm, TransparencyAnalyzerForm
from .bias_detection import detect_bias_in_data, calculate_fairness_metrics
from .transparency import analyze_model_explainability, generate_feature_importance
from .governance import get_governance_template


def index(request):
    """Main dashboard view"""
    context = {
        'title': 'AI Ethics Platform',
        'recent_analyses': ModelAnalysis.objects.order_by('-created_at')[:5],
        'case_studies_count': CaseStudy.objects.count(),
        'resources_count': EducationalResource.objects.count()
    }
    return render(request, 'dashboard/index.html', context)


def bias_detection(request):
    """Bias detection and analysis view"""
    form = ModelUploadForm()
    
    if request.method == 'POST':
        form = ModelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            model_analysis = form.save(commit=False)
            
            try:
                # Process uploaded file
                data_file = request.FILES['data_file']
                df = pd.read_csv(data_file)
                
                # Get sensitive attributes from form
                sensitive_attrs = [attr.strip() for attr in 
                                 form.cleaned_data['sensitive_attributes'].split(',')]
                
                # Detect bias in the data
                bias_results = detect_bias_in_data(df, sensitive_attrs)
                fairness_metrics = calculate_fairness_metrics(df, sensitive_attrs)
                
                # Save results to model
                model_analysis.bias_analysis = bias_results
                model_analysis.fairness_metrics = fairness_metrics
                model_analysis.save()
                
                messages.success(request, "Bias analysis completed successfully.")
                return redirect('dashboard:bias_detection')
            
            except Exception as e:
                messages.error(request, f"Error analyzing data: {str(e)}")
    
    # Get previously completed analyses
    completed_analyses = ModelAnalysis.objects.filter(
        bias_analysis__isnull=False
    ).order_by('-created_at')
    
    context = {
        'title': 'AI Bias Detection',
        'form': form,
        'completed_analyses': completed_analyses
    }
    return render(request, 'dashboard/bias_detection.html', context)


def transparency(request):
    """Model transparency and explainability view"""
    form = TransparencyAnalyzerForm()
    
    if request.method == 'POST':
        form = TransparencyAnalyzerForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Process uploaded file
                data_file = request.FILES['data_file']
                df = pd.read_csv(data_file)
                
                model_type = form.cleaned_data['model_type']
                target_column = form.cleaned_data['target_column']
                explanation_level = form.cleaned_data['explanation_level']
                
                # Generate model explainability
                explainability_results = analyze_model_explainability(
                    df, 
                    target_column,
                    model_type,
                    explanation_level
                )
                
                # Create and save analysis
                model_analysis = ModelAnalysis(
                    name=f"Transparency Analysis - {model_type}",
                    description=f"Explainability analysis with {explanation_level} detail",
                    model_type=model_type,
                    dataset_description=f"Dataset with {len(df)} records, target: {target_column}",
                    transparency_analysis=explainability_results
                )
                model_analysis.save()
                
                messages.success(request, "Transparency analysis completed successfully.")
                return redirect('dashboard:transparency')
            
            except Exception as e:
                messages.error(request, f"Error analyzing model transparency: {str(e)}")
    
    # Get previously completed transparency analyses
    completed_analyses = ModelAnalysis.objects.filter(
        transparency_analysis__isnull=False
    ).order_by('-created_at')
    
    context = {
        'title': 'AI Transparency Analyzer',
        'form': form,
        'completed_analyses': completed_analyses
    }
    return render(request, 'dashboard/transparency.html', context)


def education(request):
    """Educational resources view"""
    resources = EducationalResource.objects.all().order_by('-published_date')
    
    # Group resources by type
    grouped_resources = {}
    for resource_type, _ in EducationalResource.RESOURCE_TYPES:
        grouped_resources[resource_type] = resources.filter(resource_type=resource_type)
    
    context = {
        'title': 'AI Ethics Education',
        'grouped_resources': grouped_resources,
        'resource_types': EducationalResource.RESOURCE_TYPES
    }
    return render(request, 'dashboard/education.html', context)


def governance(request):
    """AI governance frameworks view"""
    framework_types = {
        'general': 'General AI Governance',
        'industry': 'Industry-Specific Governance',
        'regulatory': 'Regulatory Compliance',
        'fairness': 'Fairness & Bias Governance',
        'privacy': 'Privacy Governance'
    }
    
    context = {
        'title': 'AI Governance Frameworks',
        'framework_types': framework_types
    }
    return render(request, 'dashboard/governance.html', context)


def case_studies(request):
    """Case studies view"""
    all_case_studies = CaseStudy.objects.all().order_by('-published_date')
    
    # Group case studies by category
    grouped_case_studies = {}
    for category, _ in CaseStudy.CATEGORIES:
        grouped_case_studies[category] = all_case_studies.filter(category=category)
    
    context = {
        'title': 'AI Ethics Case Studies',
        'grouped_case_studies': grouped_case_studies,
        'categories': CaseStudy.CATEGORIES
    }
    return render(request, 'dashboard/case_studies.html', context)


@csrf_exempt
def analyze_bias(request):
    """API endpoint for bias analysis"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        if not request.FILES.get('data_file'):
            return JsonResponse({'error': 'No data file provided'}, status=400)
        
        data_file = request.FILES['data_file']
        df = pd.read_csv(data_file)
        
        # Get sensitive attributes from request
        sensitive_attrs = request.POST.get('sensitive_attributes', '').split(',')
        sensitive_attrs = [attr.strip() for attr in sensitive_attrs if attr.strip()]
        
        if not sensitive_attrs:
            return JsonResponse({'error': 'No sensitive attributes specified'}, status=400)
        
        # Run bias detection
        bias_results = detect_bias_in_data(df, sensitive_attrs)
        fairness_metrics = calculate_fairness_metrics(df, sensitive_attrs)
        
        return JsonResponse({
            'success': True,
            'bias_results': bias_results,
            'fairness_metrics': fairness_metrics
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def analyze_model_transparency(request):
    """API endpoint for model transparency analysis"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        if not request.FILES.get('data_file'):
            return JsonResponse({'error': 'No data file provided'}, status=400)
        
        data_file = request.FILES['data_file']
        df = pd.read_csv(data_file)
        
        model_type = request.POST.get('model_type', 'classification')
        target_column = request.POST.get('target_column', '')
        explanation_level = request.POST.get('explanation_level', 'basic')
        
        if not target_column:
            return JsonResponse({'error': 'Target column not specified'}, status=400)
        
        # Generate model explainability
        explainability_results = analyze_model_explainability(
            df, 
            target_column,
            model_type,
            explanation_level
        )
        
        return JsonResponse({
            'success': True,
            'explainability_results': explainability_results
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_governance_framework(request, framework_type):
    """API endpoint to get governance framework template"""
    if framework_type not in ['general', 'industry', 'regulatory', 'fairness', 'privacy']:
        return JsonResponse({'error': 'Invalid framework type'}, status=400)
    
    framework_template = get_governance_template(framework_type)
    
    return JsonResponse({
        'success': True,
        'framework': framework_template
    })
