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
from .bias_detection import detect_bias_in_data, calculate_fairness_metrics, perform_ai_ethics_analysis
from .transparency import analyze_model_explainability, generate_feature_importance
from .governance import get_governance_template
from . import gemini_ai
from . import sample_data


def index(request):
    """Main dashboard view"""
    # Load sample data if database is empty
    if (ModelAnalysis.objects.count() == 0 and 
        CaseStudy.objects.count() == 0 and 
        EducationalResource.objects.count() == 0):
        sample_data.populate_sample_data()
        messages.info(request, "Sample data has been loaded for demonstration purposes.")
    
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
                
                # Perform AI-powered ethics analysis
                ai_ethics_analysis = perform_ai_ethics_analysis(df, sensitive_attrs)
                
                # Merge AI analysis with bias results
                if 'error' not in ai_ethics_analysis:
                    bias_results['ai_ethics_analysis'] = ai_ethics_analysis
                
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
                
                # Add AI-powered insights for enhanced transparency
                feature_importances = {}
                if 'feature_importance' in explainability_results:
                    feature_importances = explainability_results['feature_importance']
                
                # Prepare model info for AI analysis
                model_info = {
                    'model_type': model_type,
                    'data_shape': df.shape,
                    'target_column': target_column,
                    'explanation_level': explanation_level
                }
                
                # Get AI-powered transparency insights
                try:
                    ai_transparency_insights = gemini_ai.generate_transparency_insights(
                        model_info, 
                        feature_importances
                    )
                    
                    # Add AI insights to results
                    if 'error' not in ai_transparency_insights:
                        explainability_results['ai_transparency_insights'] = ai_transparency_insights
                except Exception as ai_error:
                    # Log the error but continue without AI insights
                    print(f"AI transparency analysis error: {str(ai_error)}")
                
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
        
        # Add AI-powered ethics analysis if requested
        use_ai = request.POST.get('use_ai_analysis', 'false').lower() == 'true'
        ai_ethics_analysis = None
        
        if use_ai:
            target_column = request.POST.get('target_column', None)
            ai_ethics_analysis = perform_ai_ethics_analysis(df, sensitive_attrs, target_column)
        
        response_data = {
            'success': True,
            'bias_results': bias_results,
            'fairness_metrics': fairness_metrics
        }
        
        if ai_ethics_analysis:
            response_data['ai_ethics_analysis'] = ai_ethics_analysis
        
        return JsonResponse(response_data)
    
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
        
        # Add AI-powered transparency insights if requested
        use_ai = request.POST.get('use_ai_analysis', 'false').lower() == 'true'
        ai_transparency_insights = None
        
        if use_ai:
            # Prepare model info and feature importance for AI analysis
            model_info = {
                'model_type': model_type,
                'data_shape': df.shape,
                'target_column': target_column,
                'explanation_level': explanation_level
            }
            
            feature_importances = {}
            if 'feature_importance' in explainability_results:
                feature_importances = explainability_results['feature_importance']
            
            # Get AI-powered transparency insights
            ai_transparency_insights = gemini_ai.generate_transparency_insights(
                model_info, 
                feature_importances
            )
        
        response_data = {
            'success': True,
            'explainability_results': explainability_results
        }
        
        if ai_transparency_insights:
            response_data['ai_transparency_insights'] = ai_transparency_insights
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_governance_framework(request, framework_type):
    """API endpoint to get governance framework template"""
    if framework_type not in ['general', 'industry', 'regulatory', 'fairness', 'privacy']:
        return JsonResponse({'error': 'Invalid framework type'}, status=400)
    
    framework_template = get_governance_template(framework_type)
    
    # Check if AI-powered recommendations are requested
    use_ai = request.GET.get('use_ai_analysis', 'false').lower() == 'true'
    ai_governance_recommendations = None
    
    if use_ai:
        # Get parameters for AI recommendations
        industry = request.GET.get('industry', 'general')
        regulatory_requirements = request.GET.get('regulatory_requirements', '').split(',')
        regulatory_requirements = [req.strip() for req in regulatory_requirements if req.strip()]
        model_risk_level = request.GET.get('model_risk_level', 'medium')
        
        # Generate AI-powered governance recommendations
        ai_governance_recommendations = gemini_ai.create_governance_recommendations(
            industry,
            regulatory_requirements or ['general compliance'],
            model_risk_level
        )
    
    response_data = {
        'success': True,
        'framework': framework_template
    }
    
    if ai_governance_recommendations:
        response_data['ai_governance_recommendations'] = ai_governance_recommendations
    
    return JsonResponse(response_data)


@csrf_exempt
def analyze_fairness_metrics(request):
    """API endpoint for analyzing fairness metrics with AI insights"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Get metrics data from request
        try:
            metrics_data = json.loads(request.body)
        except:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        if not metrics_data:
            return JsonResponse({'error': 'No metrics data provided'}, status=400)
        
        # Get parameters for AI analysis
        model_type = metrics_data.get('model_type', 'classification')
        sensitive_groups = metrics_data.get('sensitive_groups', [])
        
        if not sensitive_groups:
            return JsonResponse({'error': 'No sensitive groups specified'}, status=400)
        
        # Analyze fairness metrics with AI
        analysis_results = gemini_ai.analyze_fairness_metrics(
            metrics_data,
            model_type,
            sensitive_groups
        )
        
        return JsonResponse({
            'success': True,
            'analysis_results': analysis_results
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
