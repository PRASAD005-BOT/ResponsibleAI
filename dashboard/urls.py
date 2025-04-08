from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('bias-detection/', views.bias_detection, name='bias_detection'),
    path('transparency/', views.transparency, name='transparency'),
    path('education/', views.education, name='education'),
    path('governance/', views.governance, name='governance'),
    path('case-studies/', views.case_studies, name='case_studies'),
    
    # Authentication URLs
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    
    # API endpoints
    path('api/analyze-bias/', views.analyze_bias, name='analyze_bias'),
    path('api/analyze-model-transparency/', views.analyze_model_transparency, name='analyze_model_transparency'),
    path('api/get-governance-framework/<str:framework_type>/', views.get_governance_framework, name='get_governance_framework'),
    path('api/analyze-fairness-metrics/', views.analyze_fairness_metrics, name='analyze_fairness_metrics'),
]
