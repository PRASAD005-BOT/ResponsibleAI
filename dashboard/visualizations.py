"""
Visualization utilities for AI ethics metrics
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import io
import base64

def generate_bias_visualization(bias_results):
    """
    Generates visualization data for bias results
    
    Parameters:
    -----------
    bias_results : dict
        Dictionary containing bias analysis results
        
    Returns:
    --------
    dict
        Visualization data for Charts.js
    """
    visualizations = {
        'attribute_distribution': {},
        'statistical_parity': {},
        'fairness_metrics': {},
        'risk_assessment': {}
    }
    
    # Generate attribute distribution visualizations
    if 'attribute_distribution' in bias_results:
        for attr, data in bias_results['attribute_distribution'].items():
            if 'distribution' in data:
                distribution = data['distribution']
                
                # Prepare data for Chart.js
                visualizations['attribute_distribution'][attr] = {
                    'type': 'pie',
                    'data': {
                        'labels': list(distribution.keys()),
                        'datasets': [{
                            'data': list(distribution.values()),
                            'backgroundColor': generate_colors(len(distribution))
                        }]
                    }
                }
    
    # Generate statistical parity visualizations
    if 'statistical_parity' in bias_results:
        for attr, data in bias_results['statistical_parity'].items():
            if 'positive_rates' in data:
                positive_rates = data['positive_rates']
                
                # Prepare data for Chart.js
                visualizations['statistical_parity'][attr] = {
                    'type': 'bar',
                    'data': {
                        'labels': list(positive_rates.keys()),
                        'datasets': [{
                            'label': 'Positive Rate',
                            'data': list(positive_rates.values()),
                            'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                            'borderColor': 'rgb(54, 162, 235)',
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'scales': {
                            'y': {
                                'beginAtZero': True,
                                'max': 1
                            }
                        },
                        'plugins': {
                            'title': {
                                'display': True,
                                'text': f'Statistical Parity: {attr}'
                            }
                        }
                    }
                }
    
    # Generate risk assessment visualization
    if 'overall_assessment' in bias_results:
        risk_levels = {'High risk of bias': 0, 'Medium risk of bias': 0, 'Low risk of bias': 0}
        
        for attr, data in bias_results['overall_assessment'].items():
            if 'risk_level' in data:
                risk_level = data['risk_level']
                if risk_level in risk_levels:
                    risk_levels[risk_level] += 1
        
        # Prepare data for Chart.js
        visualizations['risk_assessment'] = {
            'type': 'doughnut',
            'data': {
                'labels': list(risk_levels.keys()),
                'datasets': [{
                    'data': list(risk_levels.values()),
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.7)',  # Red for high risk
                        'rgba(255, 205, 86, 0.7)',  # Yellow for medium risk
                        'rgba(75, 192, 192, 0.7)'   # Green for low risk
                    ]
                }]
            },
            'options': {
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Overall Bias Risk Assessment'
                    }
                }
            }
        }
    
    return visualizations


def generate_fairness_visualization(fairness_metrics):
    """
    Generates visualization data for fairness metrics
    
    Parameters:
    -----------
    fairness_metrics : dict
        Dictionary containing fairness metrics
        
    Returns:
    --------
    dict
        Visualization data for Charts.js
    """
    visualizations = {
        'disparities': {},
        'group_performance': {}
    }
    
    # Generate disparity visualizations
    if 'metrics_by_attribute' in fairness_metrics:
        for attr, data in fairness_metrics['metrics_by_attribute'].items():
            if 'disparities' in data:
                disparities = data['disparities']
                
                # Prepare data for Chart.js
                visualizations['disparities'][attr] = {
                    'type': 'bar',
                    'data': {
                        'labels': list(disparities.keys()),
                        'datasets': [{
                            'label': 'Disparity',
                            'data': list(disparities.values()),
                            'backgroundColor': 'rgba(153, 102, 255, 0.5)',
                            'borderColor': 'rgb(153, 102, 255)',
                            'borderWidth': 1
                        }]
                    },
                    'options': {
                        'plugins': {
                            'title': {
                                'display': True,
                                'text': f'Fairness Metric Disparities: {attr}'
                            }
                        }
                    }
                }
            
            # Generate group performance visualizations
            if 'group_metrics' in data:
                group_metrics = data['group_metrics']
                
                # Performance metrics to visualize
                metrics = ['accuracy', 'true_positive_rate', 'false_positive_rate']
                
                for metric in metrics:
                    # Extract groups that have this metric
                    valid_groups = {}
                    for group, metrics_data in group_metrics.items():
                        if 'error' not in metrics_data and metric in metrics_data:
                            valid_groups[group] = metrics_data[metric]
                    
                    if valid_groups:
                        metric_name = {
                            'accuracy': 'Accuracy',
                            'true_positive_rate': 'True Positive Rate',
                            'false_positive_rate': 'False Positive Rate'
                        }.get(metric, metric)
                        
                        # Prepare data for Chart.js
                        key = f"{attr}_{metric}"
                        visualizations['group_performance'][key] = {
                            'type': 'bar',
                            'data': {
                                'labels': list(valid_groups.keys()),
                                'datasets': [{
                                    'label': metric_name,
                                    'data': list(valid_groups.values()),
                                    'backgroundColor': 'rgba(75, 192, 192, 0.5)',
                                    'borderColor': 'rgb(75, 192, 192)',
                                    'borderWidth': 1
                                }]
                            },
                            'options': {
                                'scales': {
                                    'y': {
                                        'beginAtZero': True,
                                        'max': 1
                                    }
                                },
                                'plugins': {
                                    'title': {
                                        'display': True,
                                        'text': f'{metric_name} by {attr}'
                                    }
                                }
                            }
                        }
    
    return visualizations


def generate_transparency_visualization(transparency_results):
    """
    Generates visualization data for model transparency analysis
    
    Parameters:
    -----------
    transparency_results : dict
        Dictionary containing transparency analysis results
        
    Returns:
    --------
    dict
        Visualization data for Charts.js
    """
    visualizations = {
        'feature_importance': {},
        'feature_interactions': {}
    }
    
    # Generate feature importance visualization
    if 'feature_importance' in transparency_results and 'feature_importance_scores' in transparency_results['feature_importance']:
        feature_scores = transparency_results['feature_importance']['feature_importance_scores']
        
        # Sort by importance
        sorted_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
        features = [item[0] for item in sorted_features]
        scores = [item[1] for item in sorted_features]
        
        # Limit to top 10 features
        if len(features) > 10:
            features = features[:10]
            scores = scores[:10]
        
        # Prepare data for Chart.js
        visualizations['feature_importance'] = {
            'type': 'horizontalBar',
            'data': {
                'labels': features,
                'datasets': [{
                    'label': 'Feature Importance',
                    'data': scores,
                    'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                    'borderColor': 'rgb(54, 162, 235)',
                    'borderWidth': 1
                }]
            },
            'options': {
                'indexAxis': 'y',
                'scales': {
                    'x': {
                        'beginAtZero': True
                    }
                },
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Feature Importance'
                    }
                }
            }
        }
    
    # Generate feature interactions visualization
    if 'feature_interactions' in transparency_results and 'potential_interactions' in transparency_results['feature_interactions']:
        interactions = transparency_results['feature_interactions']['potential_interactions']
        
        if interactions:
            interaction_labels = [' × '.join(item['features']) for item in interactions]
            interaction_strengths = [item['strength'] for item in interactions]
            
            # Prepare data for Chart.js
            visualizations['feature_interactions'] = {
                'type': 'horizontalBar',
                'data': {
                    'labels': interaction_labels,
                    'datasets': [{
                        'label': 'Interaction Strength',
                        'data': interaction_strengths,
                        'backgroundColor': 'rgba(255, 159, 64, 0.5)',
                        'borderColor': 'rgb(255, 159, 64)',
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'indexAxis': 'y',
                    'scales': {
                        'x': {
                            'beginAtZero': True
                        }
                    },
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Feature Interactions'
                        }
                    }
                }
            }
    
    return visualizations


def generate_colors(n):
    """
    Generates a list of n distinct colors
    
    Parameters:
    -----------
    n : int
        Number of colors to generate
        
    Returns:
    --------
    list
        List of color strings in rgba format
    """
    colors = [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(199, 199, 199, 0.7)',
        'rgba(83, 102, 255, 0.7)',
        'rgba(40, 159, 94, 0.7)',
        'rgba(210, 99, 132, 0.7)'
    ]
    
    if n <= len(colors):
        return colors[:n]
    
    # Generate additional colors if needed
    additional_colors = []
    for i in range(n - len(colors)):
        r = int(np.random.randint(0, 255))
        g = int(np.random.randint(0, 255))
        b = int(np.random.randint(0, 255))
        additional_colors.append(f'rgba({r}, {g}, {b}, 0.7)')
    
    return colors + additional_colors
