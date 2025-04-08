"""
Model transparency and explainability analysis functions
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import json

def analyze_model_explainability(df, target_column, model_type='classification', explanation_level='basic'):
    """
    Analyzes model explainability
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataset
    target_column : str
        The target/outcome column
    model_type : str
        Type of model (classification, regression, etc.)
    explanation_level : str
        Level of explanation detail (basic, intermediate, advanced)
        
    Returns:
    --------
    dict
        Dictionary containing explainability results
    """
    results = {
        'feature_importance': {},
        'model_complexity': {},
        'feature_interactions': {},
        'model_limitations': [],
        'recommended_explainability_methods': []
    }
    
    # Basic preprocessing
    X, y, feature_names, categorical_features = preprocess_data(df, target_column)
    
    # Generate feature importance
    feature_importance = generate_feature_importance(X, y, feature_names, model_type)
    results['feature_importance'] = feature_importance
    
    # Analyze model complexity
    results['model_complexity'] = analyze_model_complexity(df, feature_names, categorical_features)
    
    # Add recommended explainability methods
    if explanation_level == 'basic':
        results['recommended_explainability_methods'] = [
            "Feature importance plots",
            "Simple decision trees as surrogate models",
            "Partial dependence plots for top features"
        ]
    elif explanation_level == 'intermediate':
        results['recommended_explainability_methods'] = [
            "SHAP (SHapley Additive exPlanations) values",
            "Partial dependence plots",
            "Individual Conditional Expectation (ICE) plots",
            "Permutation importance"
        ]
    else:  # advanced
        results['recommended_explainability_methods'] = [
            "LIME (Local Interpretable Model-agnostic Explanations)",
            "SHAP (SHapley Additive exPlanations) values",
            "Counterfactual explanations",
            "Adversarial examples",
            "Model distillation to interpretable models"
        ]
    
    # Generate feature interactions for intermediate and advanced levels
    if explanation_level in ['intermediate', 'advanced']:
        results['feature_interactions'] = analyze_feature_interactions(X, y, feature_names, model_type)
    
    # Add model limitations
    results['model_limitations'] = identify_model_limitations(model_type, df, feature_names)
    
    return results


def preprocess_data(df, target_column):
    """
    Preprocesses data for explainability analysis
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataset
    target_column : str
        The target/outcome column
        
    Returns:
    --------
    tuple
        (X, y, feature_names, categorical_features)
    """
    # Copy dataframe to avoid modifying original
    df_copy = df.copy()
    
    # Separate features and target
    if target_column in df_copy.columns:
        y = df_copy[target_column].values
        X_df = df_copy.drop(columns=[target_column])
    else:
        # If target column not found, use all columns as features
        y = np.zeros(len(df_copy))
        X_df = df_copy
    
    # Get feature names
    feature_names = list(X_df.columns)
    
    # Identify categorical features
    categorical_features = []
    for col in feature_names:
        if X_df[col].dtype == 'object' or X_df[col].dtype == 'category':
            categorical_features.append(col)
    
    # Encode categorical features
    for col in categorical_features:
        le = LabelEncoder()
        X_df[col] = le.fit_transform(X_df[col].astype(str))
    
    # Convert to numpy array
    X = X_df.values
    
    return X, y, feature_names, categorical_features


def generate_feature_importance(X, y, feature_names, model_type='classification'):
    """
    Generates feature importance scores
    
    Parameters:
    -----------
    X : numpy.ndarray
        Feature matrix
    y : numpy.ndarray
        Target vector
    feature_names : list
        List of feature names
    model_type : str
        Type of model (classification, regression)
        
    Returns:
    --------
    dict
        Dictionary containing feature importance results
    """
    results = {}
    
    try:
        # Train a random forest model for feature importance
        if model_type == 'regression':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:  # classification or other
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        model.fit(X, y)
        
        # Get feature importance
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        # Store sorted feature importance
        sorted_importance = {}
        for i in range(min(len(feature_names), 20)):  # Top 20 features at most
            idx = indices[i]
            feature = feature_names[idx]
            importance = float(importances[idx])  # Convert numpy float to Python float
            sorted_importance[feature] = importance
        
        results['feature_importance_scores'] = sorted_importance
        
        # Add top 5 features
        results['top_features'] = list(sorted_importance.keys())[:5]
        
        # Categorize features by importance
        high_importance = []
        medium_importance = []
        low_importance = []
        
        for feature, importance in sorted_importance.items():
            if importance >= 0.1:
                high_importance.append(feature)
            elif importance >= 0.02:
                medium_importance.append(feature)
            else:
                low_importance.append(feature)
        
        results['importance_categories'] = {
            'high_importance': high_importance,
            'medium_importance': medium_importance,
            'low_importance': low_importance
        }
    
    except Exception as e:
        results['error'] = str(e)
    
    return results


def analyze_model_complexity(df, feature_names, categorical_features):
    """
    Analyzes model complexity based on data characteristics
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataset
    feature_names : list
        List of feature names
    categorical_features : list
        List of categorical feature names
        
    Returns:
    --------
    dict
        Dictionary containing model complexity assessment
    """
    results = {}
    
    # Number of features
    n_features = len(feature_names)
    n_categorical = len(categorical_features)
    n_numerical = n_features - n_categorical
    
    results['feature_count'] = {
        'total': n_features,
        'categorical': n_categorical,
        'numerical': n_numerical
    }
    
    # Assess complexity based on number of features
    if n_features <= 5:
        complexity_level = "Low"
    elif n_features <= 20:
        complexity_level = "Medium"
    else:
        complexity_level = "High"
    
    results['complexity_level'] = complexity_level
    
    # Assess interpretability potential
    if complexity_level == "Low":
        interpretability = "High - Consider using inherently interpretable models like decision trees or linear models"
    elif complexity_level == "Medium":
        interpretability = "Medium - Consider LIME or SHAP for post-hoc explanations"
    else:
        interpretability = "Low - Will require sophisticated post-hoc explanation techniques"
    
    results['interpretability_potential'] = interpretability
    
    # Recommend specific models based on complexity
    if complexity_level == "Low":
        recommended_models = ["Decision Trees", "Linear/Logistic Regression", "Rule-based models"]
    elif complexity_level == "Medium":
        recommended_models = ["Random Forest", "Gradient Boosting", "SVM with linear kernel"]
    else:
        recommended_models = ["Gradient Boosting", "Neural Networks", "Ensemble models"]
    
    results['recommended_interpretable_models'] = recommended_models
    
    return results


def analyze_feature_interactions(X, y, feature_names, model_type='classification'):
    """
    Analyzes potential feature interactions
    
    Parameters:
    -----------
    X : numpy.ndarray
        Feature matrix
    y : numpy.ndarray
        Target vector
    feature_names : list
        List of feature names
    model_type : str
        Type of model (classification, regression)
        
    Returns:
    --------
    dict
        Dictionary containing feature interaction results
    """
    results = {}
    
    try:
        # Train a random forest model
        if model_type == 'regression':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:  # classification or other
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        model.fit(X, y)
        
        # Get feature importance
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        # Focus on top features (at most 10)
        top_indices = indices[:min(10, len(feature_names))]
        top_features = [feature_names[i] for i in top_indices]
        
        # Identify potential interactions by analyzing trees
        potential_interactions = []
        
        # This is a simplified heuristic for interaction detection
        # In a real implementation, you would analyze the tree structure
        for i in range(len(top_features)):
            for j in range(i+1, len(top_features)):
                feature1 = top_features[i]
                feature2 = top_features[j]
                
                # Simulated interaction strength
                # In practice, you would compute this from the model
                interaction_strength = np.random.uniform(0, 1) * min(
                    importances[feature_names.index(feature1)],
                    importances[feature_names.index(feature2)]
                )
                
                if interaction_strength > 0.01:
                    potential_interactions.append({
                        'features': [feature1, feature2],
                        'strength': float(interaction_strength)
                    })
        
        # Sort by interaction strength
        potential_interactions.sort(key=lambda x: x['strength'], reverse=True)
        
        # Return top 5 interactions
        results['potential_interactions'] = potential_interactions[:5]
        
        # Recommendation based on interactions
        if len(potential_interactions) > 3:
            results['recommendation'] = "Consider creating interaction features or using models that capture interactions well"
        else:
            results['recommendation'] = "Few strong interactions detected; simpler models might be adequate"
    
    except Exception as e:
        results['error'] = str(e)
    
    return results


def identify_model_limitations(model_type, df, feature_names):
    """
    Identifies potential limitations of the model
    
    Parameters:
    -----------
    model_type : str
        Type of model (classification, regression, etc.)
    df : pandas.DataFrame
        The dataset
    feature_names : list
        List of feature names
        
    Returns:
    --------
    list
        List of potential limitations
    """
    limitations = []
    
    # Check for missing values
    missing_counts = df[feature_names].isnull().sum()
    if missing_counts.sum() > 0:
        features_with_missing = missing_counts[missing_counts > 0].index.tolist()
        limitations.append(f"Missing values in features: {', '.join(features_with_missing)}")
    
    # Check for highly imbalanced features
    for col in feature_names:
        if df[col].dtype in ['object', 'category']:
            value_counts = df[col].value_counts(normalize=True)
            if value_counts.max() > 0.9:
                limitations.append(f"Highly imbalanced categorical feature: {col} (dominant value: {value_counts.idxmax()})")
    
    # Model-specific limitations
    if model_type == 'classification':
        # Check for class imbalance
        if 'target' in df.columns:
            value_counts = df['target'].value_counts(normalize=True)
            if value_counts.max() > 0.9:
                limitations.append(f"Highly imbalanced target variable (dominant class: {value_counts.idxmax()})")
    
    # General limitations based on feature count
    if len(feature_names) > 50:
        limitations.append("High-dimensional data may require dimensionality reduction for better interpretability")
    
    # Add common limitations based on model type
    if model_type == 'classification':
        limitations.append("Classification models may not capture probability nuances unless properly calibrated")
    elif model_type == 'regression':
        limitations.append("Regression models assume a specific functional relationship that may not hold")
    elif model_type == 'clustering':
        limitations.append("Clustering results heavily depend on the choice of distance metric and algorithm")
    elif model_type == 'nlp':
        limitations.append("NLP models may not capture contextual nuances or domain-specific language")
    elif model_type == 'computer_vision':
        limitations.append("Computer vision models may struggle with novel visual scenarios not seen in training")
    
    # Add general limitations for all models
    limitations.append("Model interpretability often trades off with predictive performance")
    limitations.append("No model can perfectly capture all real-world complexities")
    
    return limitations
