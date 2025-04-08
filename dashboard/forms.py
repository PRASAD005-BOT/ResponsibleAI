from django import forms
from .models import ModelAnalysis

class ModelUploadForm(forms.ModelForm):
    """Form for uploading machine learning models for analysis"""
    
    class Meta:
        model = ModelAnalysis
        fields = ['name', 'description', 'model_type', 'dataset_description']
        
    data_file = forms.FileField(
        label='Dataset CSV File',
        help_text='Upload a CSV file representing your dataset',
        required=True
    )
    
    model_file = forms.FileField(
        label='Model File (optional)',
        help_text='Upload your model file if available (pickle or similar)',
        required=False
    )
    
    sensitive_attributes = forms.CharField(
        label='Sensitive Attributes',
        help_text='Comma-separated list of attributes to check for bias (e.g., gender,age,race)',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., gender,age,race'})
    )

class TransparencyAnalyzerForm(forms.Form):
    """Form for analyzing model transparency and explainability"""
    
    MODEL_TYPES = [
        ('classification', 'Classification Model'),
        ('regression', 'Regression Model'),
        ('clustering', 'Clustering Model'),
        ('nlp', 'Natural Language Processing Model'),
        ('computer_vision', 'Computer Vision Model'),
        ('other', 'Other')
    ]
    
    model_type = forms.ChoiceField(
        choices=MODEL_TYPES,
        label='Model Type',
        required=True
    )
    
    data_file = forms.FileField(
        label='Dataset CSV File',
        help_text='Upload a CSV file containing sample data',
        required=True
    )
    
    model_file = forms.FileField(
        label='Model File (optional)',
        help_text='Upload your trained model file if available',
        required=False
    )
    
    target_column = forms.CharField(
        label='Target/Outcome Column',
        help_text='Name of the column containing the target/prediction',
        required=True,
        max_length=50
    )
    
    explanation_level = forms.ChoiceField(
        choices=[
            ('basic', 'Basic (Feature Importance)'),
            ('intermediate', 'Intermediate (SHAP Values, Partial Dependence)'),
            ('advanced', 'Advanced (Full Model Explainability)')
        ],
        label='Level of Explanation',
        required=True
    )
