from django import forms
from .models import ModelAnalysis

class ModelUploadForm(forms.ModelForm):
    """Form for uploading machine learning models for analysis"""
    
    ANALYSIS_TYPE_CHOICES = [
        ('dataset', 'Upload a Dataset (CSV)'),
        ('manual', 'Enter Individual Data Manually')
    ]
    
    analysis_type = forms.ChoiceField(
        choices=ANALYSIS_TYPE_CHOICES,
        label='Analysis Type',
        required=True,
        widget=forms.RadioSelect(),
        initial='dataset'
    )
    
    class Meta:
        model = ModelAnalysis
        fields = ['name', 'description', 'model_type', 'dataset_description']
        
    data_file = forms.FileField(
        label='Dataset CSV File',
        help_text='Upload a CSV file representing your dataset',
        required=False  # Changed to False since it's only required for dataset analysis
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
    
    # Fields for manual data entry
    age = forms.IntegerField(
        label='Age',
        required=False,
        min_value=0,
        max_value=120,
        help_text='Enter age (0-120)'
    )
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-binary'),
        ('other', 'Other/Prefer not to say')
    ]
    
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label='Gender',
        required=False
    )
    
    ETHNICITY_CHOICES = [
        ('asian', 'Asian'),
        ('black', 'Black/African American'),
        ('hispanic', 'Hispanic/Latino'),
        ('middle_eastern', 'Middle Eastern'),
        ('native_american', 'Native American'),
        ('pacific_islander', 'Pacific Islander'),
        ('white', 'White/Caucasian'),
        ('multiple', 'Multiple Ethnicities'),
        ('other', 'Other/Prefer not to say')
    ]
    
    ethnicity = forms.ChoiceField(
        choices=ETHNICITY_CHOICES,
        label='Ethnicity',
        required=False
    )
    
    income = forms.IntegerField(
        label='Annual Income (USD)',
        required=False,
        min_value=0,
        help_text='Enter annual income in USD'
    )
    
    education_level = forms.ChoiceField(
        choices=[
            ('high_school', 'High School or Less'),
            ('associate', 'Associate Degree'),
            ('bachelor', 'Bachelor\'s Degree'),
            ('master', 'Master\'s Degree'),
            ('doctorate', 'Doctorate or Professional Degree'),
            ('other', 'Other/Prefer not to say')
        ],
        label='Education Level',
        required=False
    )
    
    location = forms.CharField(
        label='Location (City/Country)',
        required=False,
        max_length=100
    )
    
    employment_status = forms.ChoiceField(
        choices=[
            ('employed', 'Employed Full-time'),
            ('part_time', 'Employed Part-time'),
            ('self_employed', 'Self-employed'),
            ('unemployed', 'Unemployed'),
            ('student', 'Student'),
            ('retired', 'Retired'),
            ('other', 'Other')
        ],
        label='Employment Status',
        required=False
    )
    
    disability = forms.ChoiceField(
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
            ('prefer_not_to_say', 'Prefer not to say')
        ],
        label='Do you have a disability?',
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        analysis_type = cleaned_data.get('analysis_type')
        data_file = cleaned_data.get('data_file')
        
        if analysis_type == 'dataset' and not data_file:
            self.add_error('data_file', 'Dataset CSV file is required when using dataset analysis type')
            
        return cleaned_data

class TransparencyAnalyzerForm(forms.Form):
    """Form for analyzing model transparency and explainability"""
    
    ANALYSIS_TYPE_CHOICES = [
        ('dataset', 'Upload a Dataset (CSV)'),
        ('manual', 'Enter Individual Features Manually')
    ]
    
    analysis_type = forms.ChoiceField(
        choices=ANALYSIS_TYPE_CHOICES,
        label='Analysis Type',
        required=True,
        widget=forms.RadioSelect(),
        initial='dataset'
    )
    
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
        required=False
    )
    
    model_file = forms.FileField(
        label='Model File (optional)',
        help_text='Upload your trained model file if available',
        required=False
    )
    
    target_column = forms.CharField(
        label='Target/Outcome Column',
        help_text='Name of the column containing the target/prediction',
        required=False,
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
    
    # Manual input fields for common model features
    feature_1_name = forms.CharField(
        label='Feature 1 Name',
        required=False,
        max_length=50,
        help_text='Example: age, income, credit_score'
    )
    
    feature_1_value = forms.FloatField(
        label='Feature 1 Value',
        required=False
    )
    
    feature_2_name = forms.CharField(
        label='Feature 2 Name',
        required=False,
        max_length=50
    )
    
    feature_2_value = forms.FloatField(
        label='Feature 2 Value',
        required=False
    )
    
    feature_3_name = forms.CharField(
        label='Feature 3 Name',
        required=False,
        max_length=50
    )
    
    feature_3_value = forms.FloatField(
        label='Feature 3 Value',
        required=False
    )
    
    feature_4_name = forms.CharField(
        label='Feature 4 Name',
        required=False,
        max_length=50
    )
    
    feature_4_value = forms.FloatField(
        label='Feature 4 Value',
        required=False
    )
    
    feature_5_name = forms.CharField(
        label='Feature 5 Name',
        required=False,
        max_length=50
    )
    
    feature_5_value = forms.FloatField(
        label='Feature 5 Value',
        required=False
    )
    
    categorical_feature = forms.CharField(
        label='Categorical Feature Name',
        required=False,
        max_length=50,
        help_text='Example: gender, occupation, country'
    )
    
    categorical_value = forms.CharField(
        label='Categorical Feature Value',
        required=False,
        max_length=50,
        help_text='Example: male, manager, USA'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        analysis_type = cleaned_data.get('analysis_type')
        data_file = cleaned_data.get('data_file')
        target_column = cleaned_data.get('target_column')
        
        # Validation logic based on analysis type
        if analysis_type == 'dataset':
            if not data_file:
                self.add_error('data_file', 'Dataset CSV file is required when using dataset analysis')
            if not target_column:
                self.add_error('target_column', 'Target column is required when using dataset analysis')
        elif analysis_type == 'manual':
            # Ensure at least two features are provided for manual analysis
            feature_names = [
                cleaned_data.get('feature_1_name'),
                cleaned_data.get('feature_2_name'),
                cleaned_data.get('feature_3_name'),
                cleaned_data.get('feature_4_name'),
                cleaned_data.get('feature_5_name')
            ]
            
            feature_values = [
                cleaned_data.get('feature_1_value'),
                cleaned_data.get('feature_2_value'),
                cleaned_data.get('feature_3_value'),
                cleaned_data.get('feature_4_value'),
                cleaned_data.get('feature_5_value')
            ]
            
            valid_features = sum(1 for i in range(len(feature_names)) 
                              if feature_names[i] and feature_values[i] is not None)
            
            if valid_features < 2:
                self.add_error('feature_1_name', 'At least two features with values are required for analysis')
                
        return cleaned_data
