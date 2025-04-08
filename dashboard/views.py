from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.core.serializers.json import DjangoJSONEncoder
import json
import pandas as pd
import numpy as np
import io

# Ensure we're encoding JSON in a consistent way
class CustomJSONEncoder(DjangoJSONEncoder):
    """Custom JSON encoder that handles additional types"""
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super().default(obj)

from .models import ModelAnalysis, CaseStudy, EducationalResource, UserProfile, UserActivity
from .forms import ModelUploadForm, TransparencyAnalyzerForm, CustomSignUpForm, CustomLoginForm, UserProfileForm
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
                # Determine analysis type (dataset upload or manual input)
                analysis_type = form.cleaned_data.get('analysis_type')
                
                # Process data based on analysis type
                if analysis_type == 'dataset':
                    # Process uploaded file
                    data_file = request.FILES.get('data_file')
                    if not data_file:
                        messages.error(request, "Dataset file is required for dataset analysis")
                        return redirect('dashboard:bias_detection')
                        
                    df = pd.read_csv(data_file)
                else:  # manual input
                    # Create dataframe from manual input
                    from .bias_detection import create_dataframe_from_manual_input
                    df = create_dataframe_from_manual_input(form.cleaned_data)
                    
                    if df is None or len(df) == 0:
                        messages.error(request, "Please provide at least two attributes for manual analysis")
                        return redirect('dashboard:bias_detection')
                
                # Get sensitive attributes from form
                sensitive_attrs = [attr.strip() for attr in 
                                 form.cleaned_data['sensitive_attributes'].split(',')]
                
                # Filter sensitive attributes to only include columns that exist in the dataframe
                valid_sensitive_attrs = [attr for attr in sensitive_attrs if attr in df.columns]
                
                if not valid_sensitive_attrs:
                    if analysis_type == 'manual':
                        # For manual input, use provided demographic attributes as sensitive attributes
                        demo_attrs = ['age', 'gender', 'ethnicity', 'income', 'education_level', 
                                     'employment_status', 'disability']
                        valid_sensitive_attrs = [attr for attr in demo_attrs if attr in df.columns]
                        
                        if not valid_sensitive_attrs:
                            messages.error(request, "No valid sensitive attributes provided or found in data")
                            return redirect('dashboard:bias_detection')
                    else:
                        messages.error(request, "None of the specified sensitive attributes were found in the dataset")
                        return redirect('dashboard:bias_detection')
                
                # Get sample dataset type
                sample_dataset_type = form.cleaned_data.get('sample_dataset_type', '')
                
                try:
                    # Detect bias in the data
                    bias_results = detect_bias_in_data(df, valid_sensitive_attrs, None, sample_dataset_type)
                    
                    # Structure for minimal viable result if there are issues
                    if not isinstance(bias_results, dict):
                        bias_results = {
                            'error': 'Invalid bias results format',
                            'dataset_size': len(df),
                            'analysis_type': analysis_type
                        }
                    
                    # Calculate fairness metrics
                    fairness_metrics = calculate_fairness_metrics(df, valid_sensitive_attrs)
                    
                    # Perform AI-powered ethics analysis
                    ai_ethics_analysis = perform_ai_ethics_analysis(df, valid_sensitive_attrs, None, sample_dataset_type)
                    
                    # Merge AI analysis with bias results (safely)
                    if isinstance(ai_ethics_analysis, dict) and 'error' not in ai_ethics_analysis:
                        bias_results['ai_ethics_analysis'] = ai_ethics_analysis
                
                    # Add analysis type to results
                    bias_results['analysis_type'] = analysis_type
                    
                    # Save results to model - serialize with our custom encoder
                    bias_json = json.dumps(bias_results, cls=CustomJSONEncoder)
                    fairness_json = json.dumps(fairness_metrics, cls=CustomJSONEncoder)
                    
                    # Load back to ensure proper serialization
                    model_analysis.bias_analysis = json.loads(bias_json)
                    model_analysis.fairness_metrics = json.loads(fairness_json)
                    model_analysis.save()
                    
                except Exception as e:
                    # Create minimal valid results in case of error
                    error_message = str(e)
                    error_results = {
                        'error': f"Error in analysis: {error_message}",
                        'dataset_size': len(df),
                        'analysis_type': analysis_type
                    }
                    
                    # Serialize with custom encoder for consistency
                    error_json = json.dumps(error_results, cls=CustomJSONEncoder)
                    model_analysis.bias_analysis = json.loads(error_json)
                    model_analysis.save()
                    messages.warning(request, f"Analysis completed with errors: {error_message}")
                    return redirect('dashboard:bias_detection')
                
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
                # Determine analysis type (dataset upload or manual input)
                analysis_type = form.cleaned_data.get('analysis_type')
                model_type = form.cleaned_data['model_type']
                explanation_level = form.cleaned_data['explanation_level']
                
                # Process data based on analysis type
                if analysis_type == 'dataset':
                    # Process uploaded file
                    data_file = request.FILES.get('data_file')
                    if not data_file:
                        messages.error(request, "Dataset file is required for dataset analysis")
                        return redirect('dashboard:transparency')
                        
                    df = pd.read_csv(data_file)
                    target_column = form.cleaned_data.get('target_column')
                    
                    if not target_column or target_column not in df.columns:
                        messages.error(request, "Please specify a valid target column in the dataset")
                        return redirect('dashboard:transparency')
                else:  # manual input
                    # Create dataframe from manually entered features
                    data = {}
                    
                    # Extract feature names and values
                    feature_names = []
                    feature_values = []
                    
                    for i in range(1, 6):
                        name_key = f'feature_{i}_name'
                        value_key = f'feature_{i}_value'
                        
                        name = form.cleaned_data.get(name_key)
                        value = form.cleaned_data.get(value_key)
                        
                        if name and value is not None:
                            feature_names.append(name)
                            feature_values.append(value)
                            data[name] = [value]
                    
                    # Add categorical feature if provided
                    cat_feature = form.cleaned_data.get('categorical_feature')
                    cat_value = form.cleaned_data.get('categorical_value')
                    
                    if cat_feature and cat_value:
                        data[cat_feature] = [cat_value]
                        feature_names.append(cat_feature)
                    
                    if len(feature_names) < 2:
                        messages.error(request, "Please provide at least two features for analysis")
                        return redirect('dashboard:transparency')
                    
                    # Create a target column for analysis
                    target_column = 'synthesized_target'
                    
                    # Create a simple synthetic target based on the first feature
                    # This is just for demonstration purposes
                    first_feature_value = feature_values[0]
                    threshold = first_feature_value * 0.75  # Arbitrary threshold
                    
                    if model_type == 'classification':
                        # Binary classification target
                        data[target_column] = [1 if first_feature_value > threshold else 0]
                    else:
                        # Regression target (scaled version of first feature)
                        data[target_column] = [first_feature_value * 1.5]
                    
                    # Create the dataframe
                    df = pd.DataFrame(data)
                    
                    # Generate a small synthetic dataset for context
                    # Add 20 rows with slightly varied data
                    for _ in range(20):
                        row = {}
                        for name, value in zip(feature_names, feature_values):
                            if isinstance(value, (int, float)):
                                # Add random variation around the original value
                                variation = value * 0.2  # 20% variation
                                row[name] = value + np.random.uniform(-variation, variation)
                            else:
                                row[name] = value
                        
                        # Add categorical feature if provided
                        if cat_feature and cat_value:
                            row[cat_feature] = cat_value
                        
                        # Add target value
                        if model_type == 'classification':
                            # Synthetic classification target
                            first_feat_with_noise = row.get(feature_names[0], 0) * (1 + np.random.normal(0, 0.1))
                            row[target_column] = 1 if first_feat_with_noise > threshold else 0
                        else:
                            # Synthetic regression target
                            first_feat_with_noise = row.get(feature_names[0], 0) * (1 + np.random.normal(0, 0.1))
                            row[target_column] = first_feat_with_noise * 1.5
                        
                        # Append to dataframe
                        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                
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
                
                # Add analysis type to results
                explainability_results['analysis_type'] = analysis_type
                
                # Prepare model info for AI analysis
                model_info = {
                    'model_type': model_type,
                    'data_shape': df.shape,
                    'target_column': target_column,
                    'explanation_level': explanation_level,
                    'analysis_type': analysis_type
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


def user_signup(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log the activity
            UserActivity.objects.create(
                user=user,
                activity_type='account_created',
                description='User account created'
            )
            
            # Authenticate and log in the user
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            
            messages.success(request, "Your account has been created successfully!")
            return redirect('dashboard:index')
    else:
        form = CustomSignUpForm()
    
    context = {
        'title': 'Sign Up - AI Ethics Platform',
        'form': form
    }
    return render(request, 'dashboard/signup.html', context)


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Log the activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='login',
                    description='User logged in'
                )
                
                # Redirect to the page they were trying to access, or homepage
                next_page = request.GET.get('next', 'dashboard:index')
                messages.success(request, "You have been logged in successfully!")
                return redirect(next_page)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomLoginForm()
    
    context = {
        'title': 'Login - AI Ethics Platform',
        'form': form
    }
    return render(request, 'dashboard/login.html', context)


def user_logout(request):
    """User logout view"""
    if request.user.is_authenticated:
        # Log the activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='logout',
            description='User logged out'
        )
    
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('dashboard:index')


@login_required
def user_profile(request):
    """User profile view"""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user.profile, user=user)
        if form.is_valid():
            form.save()
            
            # Log the activity
            UserActivity.objects.create(
                user=user,
                activity_type='profile_updated',
                description='User profile updated'
            )
            
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('dashboard:profile')
    else:
        form = UserProfileForm(instance=user.profile, user=user)
    
    # Get user's model analyses
    user_analyses = ModelAnalysis.objects.filter(user=user).order_by('-created_at')
    
    # Get user's recent activities
    user_activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:10]
    
    context = {
        'title': 'My Profile - AI Ethics Platform',
        'form': form,
        'user_analyses': user_analyses,
        'user_activities': user_activities
    }
    return render(request, 'dashboard/profile.html', context)


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
        
        # Use custom encoder to ensure proper serialization of numpy types
        return JsonResponse(response_data, encoder=CustomJSONEncoder)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500, encoder=CustomJSONEncoder)


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
        
        # Use custom encoder to ensure proper serialization of numpy types
        return JsonResponse(response_data, encoder=CustomJSONEncoder)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, encoder=CustomJSONEncoder)


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
    
    # Use custom encoder to ensure proper serialization of numpy types
    return JsonResponse(response_data, encoder=CustomJSONEncoder)


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
        }, encoder=CustomJSONEncoder)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, encoder=CustomJSONEncoder)
