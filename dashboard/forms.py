from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ModelAnalysis, UserProfile

class BaseForm:
    """Base form class with CSRF protection compatibility"""
    @property
    def hidden_tag(self):
        """Compatibility method for templates that use Flask-style form.hidden_tag()"""
        # This is just a no-op in Django as csrf_token template tag handles this
        return ""

class CustomSignUpForm(UserCreationForm, BaseForm):
    """Extended user registration form"""
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    organization = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    job_title = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'organization', 'job_title')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Update user profile
            user.profile.organization = self.cleaned_data.get('organization', '')
            user.profile.job_title = self.cleaned_data.get('job_title', '')
            user.profile.save()
            
        return user

class CustomLoginForm(AuthenticationForm, BaseForm):
    """Enhanced login form with styling"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class UserProfileForm(forms.ModelForm, BaseForm):
    """Form for editing user profile information"""
    
    INDUSTRY_CHOICES = [
        ('', 'Select Industry'),
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance & Banking'),
        ('education', 'Education'),
        ('government', 'Government'),
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('consulting', 'Consulting'),
        ('nonprofit', 'Non-profit'),
        ('research', 'Research'),
        ('other', 'Other')
    ]
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    organization = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    job_title = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    industry = forms.ChoiceField(
        choices=INDUSTRY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
    
    interests = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., bias detection, transparency, AI governance'})
    )
    
    class Meta:
        model = UserProfile
        fields = ['organization', 'job_title', 'industry', 'bio', 'interests']
    
    def __init__(self, *args, **kwargs):
        # Get the user from kwargs
        self.user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        # If we have a user, load their data
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Update the related User model
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            
            if commit:
                self.user.save()
                profile.save()
        
        return profile

class ModelUploadForm(forms.ModelForm, BaseForm):
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

class TransparencyAnalyzerForm(forms.Form, BaseForm):
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
