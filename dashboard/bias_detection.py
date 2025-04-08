"""
Bias detection and fairness metrics calculation for AI models
Includes Gemini AI-powered analysis for enhanced ethical insights
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix
import scipy.stats as stats

# Import Gemini AI module
from . import gemini_ai

def create_dataframe_from_manual_input(form_data):
    """
    Creates a pandas DataFrame from manually entered form data
    
    Parameters:
    -----------
    form_data : dict
        Dictionary containing form data from the frontend
        
    Returns:
    --------
    pandas.DataFrame
        A DataFrame constructed from the manual input
    """
    # Initialize empty data dictionary
    data = {}
    
    # Extract common demographic attributes
    if form_data.get('age'):
        data['age'] = [form_data.get('age')]
        
    if form_data.get('gender'):
        data['gender'] = [form_data.get('gender')]
        
    if form_data.get('ethnicity'):
        data['ethnicity'] = [form_data.get('ethnicity')]
        
    if form_data.get('income'):
        data['income'] = [form_data.get('income')]
        
    if form_data.get('education_level'):
        data['education_level'] = [form_data.get('education_level')]
        
    if form_data.get('location'):
        data['location'] = [form_data.get('location')]
        
    if form_data.get('employment_status'):
        data['employment_status'] = [form_data.get('employment_status')]
        
    if form_data.get('disability'):
        data['disability'] = [form_data.get('disability')]
    
    # Create example population data for comparison
    # We use the user's input as a single data point and add synthetic comparison data
    # This is necessary for bias detection which requires multiple data points
    
    # Create a DataFrame with the user's data
    user_df = pd.DataFrame(data)
    
    if len(user_df.columns) == 0:
        # No valid data provided
        return None
    
    # Create a sample population for comparison
    # This is a minimal approach - we just need some comparison points
    population_size = 100
    complete_df = user_df.copy()
    
    # For each column, generate similar but slightly varied data
    for column in user_df.columns:
        if column == 'age' and 'age' in user_df.columns:
            # Generate age distribution centered around user's age with reasonable spread
            user_age = user_df['age'].iloc[0]
            age_std = 10  # standard deviation for age distribution
            ages = np.random.normal(user_age, age_std, population_size)
            ages = np.clip(ages, 18, 90).astype(int)  # clip to reasonable range
            complete_df[column] = ages
            
        elif column == 'income' and 'income' in user_df.columns:
            # Generate income distribution
            user_income = user_df['income'].iloc[0]
            income_std = user_income * 0.3  # 30% standard deviation
            incomes = np.random.normal(user_income, income_std, population_size)
            incomes = np.clip(incomes, 0, None).astype(int)
            complete_df[column] = incomes
            
        elif column in ['gender', 'ethnicity', 'education_level', 'employment_status', 'disability']:
            # For categorical variables, create a realistic distribution
            user_value = user_df[column].iloc[0]
            
            # Create distribution where user's value has higher probability
            categories = get_category_values(column)
            probabilities = [0.1] * len(categories)
            
            # User's category gets higher probability
            user_idx = categories.index(user_value) if user_value in categories else 0
            probabilities[user_idx] = 0.5
            
            # Normalize probabilities
            probabilities = [p/sum(probabilities) for p in probabilities]
            
            # Generate population data
            complete_df[column] = np.random.choice(
                categories, 
                size=population_size, 
                p=probabilities
            )
            
        elif column == 'location' and 'location' in user_df.columns:
            # For location, we just duplicate the user's value
            complete_df[column] = user_df[column].iloc[0]
            
    return complete_df

def get_category_values(column_name):
    """
    Return possible values for categorical variables
    
    Parameters:
    -----------
    column_name : str
        Name of the categorical column
        
    Returns:
    --------
    list
        List of possible values for the category
    """
    categories = {
        'gender': ['male', 'female', 'non_binary', 'other'],
        'ethnicity': ['asian', 'black', 'hispanic', 'middle_eastern', 
                     'native_american', 'pacific_islander', 'white', 
                     'multiple', 'other'],
        'education_level': ['high_school', 'associate', 'bachelor', 
                          'master', 'doctorate', 'other'],
        'employment_status': ['employed', 'part_time', 'self_employed', 
                            'unemployed', 'student', 'retired', 'other'],
        'disability': ['yes', 'no', 'prefer_not_to_say']
    }
    
    return categories.get(column_name, ['unknown'])

def detect_bias_in_data(df, sensitive_attributes, target_column=None):
    """
    Detects potential bias in data based on sensitive attributes
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataset to analyze
    sensitive_attributes : list
        List of column names that contain sensitive attributes
    target_column : str, optional
        Target/outcome column if available
        
    Returns:
    --------
    dict
        Dictionary containing bias detection results
    """
    results = {
        'dataset_size': len(df),
        'attribute_distribution': {},
        'correlation_with_sensitive': {},
        'statistical_parity': {},
        'overall_assessment': {}
    }
    
    # Check distribution of sensitive attributes
    for attr in sensitive_attributes:
        if attr not in df.columns:
            results['attribute_distribution'][attr] = {
                'error': f"Column {attr} not found in dataset"
            }
            continue
        
        # Calculate distribution
        distribution = df[attr].value_counts(normalize=True).to_dict()
        results['attribute_distribution'][attr] = {
            'distribution': distribution,
            'entropy': stats.entropy(list(distribution.values())),
            'unique_values': len(distribution)
        }
        
        # Add assessment
        if max(distribution.values()) > 0.8:
            results['attribute_distribution'][attr]['assessment'] = "Highly imbalanced"
        elif max(distribution.values()) > 0.6:
            results['attribute_distribution'][attr]['assessment'] = "Moderately imbalanced"
        else:
            results['attribute_distribution'][attr]['assessment'] = "Relatively balanced"
    
    # If target column provided, check for correlation with sensitive attributes
    if target_column and target_column in df.columns:
        for attr in sensitive_attributes:
            if attr not in df.columns:
                continue
                
            # For categorical target, check chi-square
            if df[target_column].dtype == 'object' or df[target_column].dtype == 'category':
                try:
                    contingency = pd.crosstab(df[attr], df[target_column])
                    chi2, p, _, _ = stats.chi2_contingency(contingency)
                    correlation = {
                        'method': 'chi_square',
                        'chi2': chi2,
                        'p_value': p,
                        'significant': p < 0.05
                    }
                except:
                    correlation = {
                        'method': 'chi_square',
                        'error': 'Could not calculate chi-square'
                    }
            # For numerical target, check correlation
            else:
                try:
                    # Convert categorical attributes to numerical
                    if df[attr].dtype == 'object' or df[attr].dtype == 'category':
                        le = LabelEncoder()
                        attr_encoded = le.fit_transform(df[attr])
                        corr, p = stats.pearsonr(attr_encoded, df[target_column])
                    else:
                        corr, p = stats.pearsonr(df[attr], df[target_column])
                    
                    correlation = {
                        'method': 'pearson',
                        'correlation': corr,
                        'p_value': p,
                        'significant': p < 0.05
                    }
                except:
                    correlation = {
                        'method': 'pearson',
                        'error': 'Could not calculate correlation'
                    }
            
            results['correlation_with_sensitive'][attr] = correlation
            
            # Calculate statistical parity if binary target
            if len(df[target_column].unique()) == 2:
                try:
                    parity_results = check_statistical_parity(df, attr, target_column)
                    results['statistical_parity'][attr] = parity_results
                except Exception as e:
                    results['statistical_parity'][attr] = {
                        'error': str(e)
                    }
    
    # Overall assessment
    for attr in sensitive_attributes:
        if attr not in df.columns:
            continue
            
        # Check for potential bias
        bias_indicators = []
        
        # Imbalanced distribution
        if attr in results['attribute_distribution'] and 'assessment' in results['attribute_distribution'][attr]:
            if results['attribute_distribution'][attr]['assessment'] in ["Highly imbalanced", "Moderately imbalanced"]:
                bias_indicators.append("Imbalanced distribution")
        
        # Correlation with target
        if attr in results['correlation_with_sensitive']:
            if 'significant' in results['correlation_with_sensitive'][attr] and results['correlation_with_sensitive'][attr]['significant']:
                bias_indicators.append("Significant correlation with target")
        
        # Statistical parity difference
        if attr in results['statistical_parity'] and 'parity_difference' in results['statistical_parity'][attr]:
            if abs(results['statistical_parity'][attr]['parity_difference']) > 0.1:
                bias_indicators.append("Statistical parity difference exceeds 0.1")
        
        # Set overall assessment
        if len(bias_indicators) >= 2:
            risk_level = "High risk of bias"
        elif len(bias_indicators) == 1:
            risk_level = "Medium risk of bias"
        else:
            risk_level = "Low risk of bias"
            
        results['overall_assessment'][attr] = {
            'risk_level': risk_level,
            'bias_indicators': bias_indicators
        }
    
    return results


def check_statistical_parity(df, sensitive_attr, target_column):
    """
    Checks statistical parity (difference in positive outcomes between groups)
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataset to analyze
    sensitive_attr : str
        Column name of the sensitive attribute
    target_column : str
        Target/outcome column
        
    Returns:
    --------
    dict
        Dictionary containing statistical parity results
    """
    results = {}
    
    # Get unique values in sensitive attribute
    unique_attrs = df[sensitive_attr].unique()
    
    # Check parity for each value
    positive_rates = {}
    for attr_value in unique_attrs:
        subset = df[df[sensitive_attr] == attr_value]
        positive_rate = subset[target_column].mean()
        positive_rates[attr_value] = positive_rate
    
    # Calculate parity difference (max difference between groups)
    max_rate = max(positive_rates.values())
    min_rate = min(positive_rates.values())
    parity_difference = max_rate - min_rate
    
    results['positive_rates'] = positive_rates
    results['parity_difference'] = parity_difference
    
    # Assess parity
    if parity_difference <= 0.05:
        results['assessment'] = "Good statistical parity"
    elif parity_difference <= 0.1:
        results['assessment'] = "Moderate statistical parity"
    else:
        results['assessment'] = "Poor statistical parity"
    
    return results


def perform_ai_ethics_analysis(df, sensitive_attributes, target_column=None):
    """
    Uses Google Gemini AI to perform advanced ethical analysis on dataset
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataset to analyze
    sensitive_attributes : list
        List of column names that contain sensitive attributes
    target_column : str, optional
        Target/outcome column if available
        
    Returns:
    --------
    dict
        AI-generated ethics analysis results
    """
    try:
        # Prepare dataset info for the AI
        df_info = {
            'columns': list(df.columns),
            'shape': df.shape,
            'data_types': {col: str(df[col].dtype) for col in df.columns},
            'missing_values': {col: int(df[col].isna().sum()) for col in df.columns},
            'sample_rows': df.head(5).to_dict(orient='records'),
            'statistics': {}
        }
        
        # Add statistics for each column
        for col in df.columns:
            if df[col].dtype.kind in 'ifc':  # numeric columns
                df_info['statistics'][col] = {
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'std': float(df[col].std())
                }
            else:  # categorical columns
                df_info['statistics'][col] = {
                    'unique_values': int(df[col].nunique()),
                    'most_common': df[col].value_counts().nlargest(3).to_dict()
                }
        
        # Add target column info if available
        if target_column and target_column in df.columns:
            df_info['target_column'] = {
                'name': target_column,
                'type': str(df[target_column].dtype),
                'distribution': df[target_column].value_counts().to_dict() if df[target_column].dtype.kind not in 'ifc' else None
            }
        
        # Call Gemini AI for analysis
        ai_analysis = gemini_ai.analyze_dataset_ethics(df_info, sensitive_attributes)
        return ai_analysis
        
    except Exception as e:
        # Return error information if AI analysis fails
        return {
            'error': str(e),
            'message': 'AI-powered ethics analysis could not be completed'
        }

def calculate_fairness_metrics(df, sensitive_attributes, target_column=None, prediction_column=None):
    """
    Calculates fairness metrics for model predictions
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataset containing target and predictions
    sensitive_attributes : list
        List of column names that contain sensitive attributes
    target_column : str, optional
        Actual outcome column
    prediction_column : str, optional
        Predicted outcome column
        
    Returns:
    --------
    dict
        Dictionary containing fairness metrics
    """
    results = {
        'metrics_by_attribute': {}
    }
    
    # If no prediction column, we can only do limited analysis
    if target_column is None or prediction_column is None:
        # Only do limited analysis
        for attr in sensitive_attributes:
            if attr not in df.columns:
                continue
                
            results['metrics_by_attribute'][attr] = {
                'note': 'Limited analysis - prediction or target column not provided'
            }
            
            # Check distribution
            distribution = df[attr].value_counts(normalize=True).to_dict()
            results['metrics_by_attribute'][attr]['distribution'] = distribution
        
        return results
    
    # Full analysis with target and prediction columns
    for attr in sensitive_attributes:
        if attr not in df.columns:
            continue
            
        attr_results = {}
        
        # Get unique values in sensitive attribute
        unique_attrs = df[attr].unique()
        
        # Calculate metrics for each group
        group_metrics = {}
        for attr_value in unique_attrs:
            subset = df[df[attr] == attr_value]
            
            # Skip if too few samples
            if len(subset) < 10:
                group_metrics[attr_value] = {
                    'error': 'Too few samples'
                }
                continue
            
            # Calculate confusion matrix
            y_true = subset[target_column]
            y_pred = subset[prediction_column]
            
            try:
                tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
                
                # Calculate metrics
                group_metrics[attr_value] = {
                    'sample_size': len(subset),
                    'true_positive_rate': tp / (tp + fn) if (tp + fn) > 0 else 0,
                    'false_positive_rate': fp / (fp + tn) if (fp + tn) > 0 else 0,
                    'true_negative_rate': tn / (tn + fp) if (tn + fp) > 0 else 0,
                    'false_negative_rate': fn / (fn + tp) if (fn + tp) > 0 else 0,
                    'positive_predictive_value': tp / (tp + fp) if (tp + fp) > 0 else 0,
                    'accuracy': (tp + tn) / (tp + tn + fp + fn)
                }
            except:
                group_metrics[attr_value] = {
                    'error': 'Could not calculate metrics'
                }
        
        attr_results['group_metrics'] = group_metrics
        
        # Calculate disparities
        if len(group_metrics) >= 2:
            # Calculate disparities for each metric
            disparities = {
                'true_positive_rate': [],
                'false_positive_rate': [],
                'accuracy': []
            }
            
            valid_groups = [g for g in group_metrics if 'error' not in group_metrics[g]]
            
            if len(valid_groups) >= 2:
                for metric in disparities:
                    values = [group_metrics[g][metric] for g in valid_groups]
                    max_disparity = max(values) - min(values)
                    disparities[metric] = max_disparity
                
                attr_results['disparities'] = disparities
                
                # Overall fairness assessment
                tpr_disparity = disparities['true_positive_rate']
                fpr_disparity = disparities['false_positive_rate']
                
                if tpr_disparity <= 0.1 and fpr_disparity <= 0.1:
                    fairness_assessment = "Good fairness"
                elif tpr_disparity <= 0.2 and fpr_disparity <= 0.2:
                    fairness_assessment = "Moderate fairness"
                else:
                    fairness_assessment = "Poor fairness"
                
                attr_results['fairness_assessment'] = fairness_assessment
        
        results['metrics_by_attribute'][attr] = attr_results
    
    return results
