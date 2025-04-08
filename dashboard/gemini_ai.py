"""
Google Gemini integration for AI ethics analysis
Provides AI-powered insights for model bias, transparency, and governance
"""

import json
import google.generativeai as genai
from django.conf import settings

# Initialize Gemini API with key from Django settings
GOOGLE_GEMINI_API_KEY = settings.GOOGLE_GEMINI_API_KEY
MODEL_NAME = settings.GEMINI_MODEL_NAME

# Configure the Gemini API
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

def analyze_dataset_ethics(df_info, sensitive_attributes, sample_dataset_type=None):
    """
    Analyzes a dataset for potential ethical issues
    
    Parameters:
    -----------
    df_info : dict
        Dictionary with dataset information (columns, sample rows, statistics)
    sensitive_attributes : list
        List of column names that contain sensitive attributes
    sample_dataset_type : str, optional
        Type of dataset being analyzed (e.g., 'hiring_dataset', 'loan_approval')
        
    Returns:
    --------
    dict
        Analysis results including ethical insights
    """
    # Prepare the prompt with dataset information
    prompt = f"""
    Analyze this dataset for potential ethical issues and bias:
    
    Dataset Info: {json.dumps(df_info, indent=2)}
    
    Sensitive Attributes: {', '.join(sensitive_attributes)}
    
    Dataset Type: {sample_dataset_type if sample_dataset_type else 'Not specified'}
    
    Please provide:
    1. Potential ethical concerns in this dataset
    2. Bias patterns that might exist related to sensitive attributes
    3. Data representation issues (missing groups, imbalanced classes)
    4. Recommendations for mitigating these issues
    5. Ethical considerations for model deployment
    
    Format your response as a detailed ethics analysis suitable for a business audience.
    """
    
    # Generate AI response
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    
    # Process and structure the response
    analysis = {
        "ethical_concerns": extract_section(response.text, "ethical concerns"),
        "bias_patterns": extract_section(response.text, "bias patterns"),
        "representation_issues": extract_section(response.text, "representation issues"),
        "recommendations": extract_section(response.text, "recommendations"),
        "deployment_considerations": extract_section(response.text, "deployment"),
        "full_analysis": response.text
    }
    
    return analysis

def generate_transparency_insights(model_info, feature_importances):
    """
    Generates insights to improve model transparency and explainability
    
    Parameters:
    -----------
    model_info : dict
        Dictionary with model information
    feature_importances : dict
        Dictionary with feature importance scores
        
    Returns:
    --------
    dict
        Transparency insights and recommendations
    """
    # Prepare the prompt with model information
    prompt = f"""
    Analyze this AI model's transparency and provide insights:
    
    Model Info: {json.dumps(model_info, indent=2)}
    
    Feature Importances: {json.dumps(feature_importances, indent=2)}
    
    Please provide:
    1. An assessment of this model's explainability
    2. Key features driving model decisions and their ethical implications
    3. Transparency gaps that should be addressed
    4. Recommendations for improving model explainability
    5. Stakeholder communication strategies for explaining this model
    
    Format your response as actionable transparency insights for business stakeholders.
    """
    
    # Generate AI response
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    
    # Process and structure the response
    insights = {
        "explainability_assessment": extract_section(response.text, "explainability"),
        "key_features_analysis": extract_section(response.text, "key features"),
        "transparency_gaps": extract_section(response.text, "transparency gaps"),
        "improvement_recommendations": extract_section(response.text, "recommendations"),
        "communication_strategies": extract_section(response.text, "communication"),
        "full_insights": response.text
    }
    
    return insights

def create_governance_recommendations(industry, regulatory_requirements, model_risk_level):
    """
    Creates customized AI governance recommendations
    
    Parameters:
    -----------
    industry : str
        The industry sector (e.g., finance, healthcare)
    regulatory_requirements : list
        List of regulatory frameworks to consider
    model_risk_level : str
        Risk level of the model (low, medium, high)
        
    Returns:
    --------
    dict
        Customized governance recommendations
    """
    # Prepare the prompt with governance information
    prompt = f"""
    Create AI governance recommendations for:
    
    Industry: {industry}
    Regulatory Requirements: {', '.join(regulatory_requirements)}
    Model Risk Level: {model_risk_level}
    
    Please provide:
    1. Customized governance framework for this context
    2. Documentation requirements and templates
    3. Testing and validation protocols
    4. Monitoring and audit procedures
    5. Roles and responsibilities for ethical oversight
    
    Format your response as an actionable governance plan for business implementation.
    """
    
    # Generate AI response
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    
    # Process and structure the response
    recommendations = {
        "governance_framework": extract_section(response.text, "governance framework"),
        "documentation_requirements": extract_section(response.text, "documentation"),
        "testing_protocols": extract_section(response.text, "testing"),
        "monitoring_procedures": extract_section(response.text, "monitoring"),
        "roles_responsibilities": extract_section(response.text, "roles"),
        "full_recommendations": response.text
    }
    
    return recommendations

def analyze_fairness_metrics(metrics_data, model_type, sensitive_groups):
    """
    Analyzes fairness metrics and provides interpretation
    
    Parameters:
    -----------
    metrics_data : dict
        Dictionary with fairness metrics results
    model_type : str
        Type of model being analyzed
    sensitive_groups : list
        List of sensitive demographic groups
        
    Returns:
    --------
    dict
        Fairness analysis and recommendations
    """
    # Prepare the prompt with metrics information
    prompt = f"""
    Analyze these fairness metrics and provide business-friendly interpretation:
    
    Metrics Data: {json.dumps(metrics_data, indent=2)}
    Model Type: {model_type}
    Sensitive Groups: {', '.join(sensitive_groups)}
    
    Please provide:
    1. Interpretation of these fairness metrics in plain language
    2. Assessment of disparate impact across sensitive groups
    3. Comparison to ethical and regulatory standards
    4. Specific recommendations to improve fairness
    5. Business implications of these fairness results
    
    Format your response as an actionable fairness analysis for non-technical stakeholders.
    """
    
    # Generate AI response
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    
    # Process and structure the response
    analysis = {
        "metrics_interpretation": extract_section(response.text, "interpretation"),
        "disparate_impact": extract_section(response.text, "disparate impact"),
        "standards_comparison": extract_section(response.text, "standards"),
        "fairness_recommendations": extract_section(response.text, "recommendations"),
        "business_implications": extract_section(response.text, "implications"),
        "full_analysis": response.text
    }
    
    return analysis

def extract_section(text, section_keyword):
    """
    Extracts a section from the AI response text
    
    Parameters:
    -----------
    text : str
        Full AI response text
    section_keyword : str
        Keyword to identify the section
        
    Returns:
    --------
    str
        Extracted section text
    """
    paragraphs = text.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        if section_keyword.lower() in paragraph.lower():
            # Try to return this paragraph and the following one
            if i < len(paragraphs) - 1:
                return paragraph + '\n\n' + paragraphs[i+1]
            return paragraph
    
    # If section not clearly identified, return a general extract
    words = text.split()
    if len(words) > 100:
        return ' '.join(words[:100]) + '...'
    return text