/**
 * AI Ethics Platform - Bias Detection Dashboard
 * Handles functionality for bias detection and visualization
 */

let biasCharts = {};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize bias detection form
    const biasForm = document.getElementById('bias-detection-form');
    if (biasForm) {
        initBiasDetectionForm();
    }
    
    // Initialize existing bias analysis visualizations
    const biasAnalyses = document.querySelectorAll('.bias-analysis');
    if (biasAnalyses.length > 0) {
        initExistingBiasVisualizations();
    }
});

/**
 * Initialize the bias detection form
 */
function initBiasDetectionForm() {
    const form = document.getElementById('bias-detection-form');
    const fileInput = document.getElementById('id_data_file');
    const fileLabel = document.querySelector('.file-input-label');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Add file input change handler
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                fileLabel.textContent = fileInput.files[0].name;
            } else {
                fileLabel.textContent = 'Choose a file...';
            }
        });
    }
    
    // Add form submit handler
    form.addEventListener('submit', function(e) {
        // Show loading state
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner"></span> Analyzing...';
        }
        
        // Regular form submission will continue
    });
    
    // Initialize sensitive attributes suggestions
    initSensitiveAttributesSuggestions();
}

/**
 * Initialize suggestions for sensitive attributes field
 */
function initSensitiveAttributesSuggestions() {
    const sensAttrField = document.getElementById('id_sensitive_attributes');
    if (!sensAttrField) return;
    
    const commonAttributes = [
        'gender', 'age', 'race', 'ethnicity', 'religion', 
        'disability', 'marital_status', 'income', 'education',
        'nationality', 'sexual_orientation', 'postal_code'
    ];
    
    // Create and add suggestion buttons
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'attribute-suggestions mt-2';
    
    // Add heading
    const heading = document.createElement('small');
    heading.className = 'text-muted';
    heading.textContent = 'Suggested attributes:';
    suggestionsContainer.appendChild(heading);
    
    // Add suggestion buttons
    commonAttributes.forEach(attr => {
        const badge = document.createElement('span');
        badge.className = 'badge badge-primary attribute-suggestion';
        badge.textContent = attr;
        badge.style.cursor = 'pointer';
        badge.addEventListener('click', function() {
            // Get current value
            let currentValue = sensAttrField.value.trim();
            
            // Add the attribute if it's not already there
            if (currentValue === '') {
                sensAttrField.value = attr;
            } else {
                // Check if attribute already exists
                const attrs = currentValue.split(',').map(a => a.trim());
                if (!attrs.includes(attr)) {
                    sensAttrField.value = currentValue + ', ' + attr;
                }
            }
        });
        
        suggestionsContainer.appendChild(badge);
    });
    
    // Add to the DOM after the field
    sensAttrField.parentNode.insertBefore(suggestionsContainer, sensAttrField.nextSibling);
}

/**
 * Initialize visualizations for existing bias analyses
 */
function initExistingBiasVisualizations() {
    const biasAnalyses = document.querySelectorAll('.bias-analysis');
    
    biasAnalyses.forEach(analysis => {
        try {
            // Get analysis data
            const analysisId = analysis.getAttribute('data-analysis-id');
            const biasResultsStr = analysis.getAttribute('data-bias-results');
            const fairnessMetricsStr = analysis.getAttribute('data-fairness-metrics');
            
            // Parse JSON data
            const biasResults = JSON.parse(biasResultsStr);
            const fairnessMetrics = fairnessMetricsStr ? JSON.parse(fairnessMetricsStr) : null;
            
            // Create visualizations
            createBiasVisualizations(analysisId, biasResults, fairnessMetrics);
            
            // Show additional information
            populateBiasAnalysisSummary(analysisId, biasResults, fairnessMetrics);
            
        } catch (error) {
            console.error('Error initializing bias visualization:', error);
        }
    });
}

/**
 * Create bias detection visualizations
 * @param {string} analysisId - ID of the analysis
 * @param {Object} biasResults - Bias analysis results
 * @param {Object} fairnessMetrics - Fairness metrics results
 */
function createBiasVisualizations(analysisId, biasResults, fairnessMetrics) {
    if (!biasResults || !analysisId) return;
    
    // Get visualization containers
    const distributionContainer = document.getElementById(`distribution-charts-${analysisId}`);
    const parityContainer = document.getElementById(`parity-charts-${analysisId}`);
    const metricsContainer = document.getElementById(`fairness-metrics-${analysisId}`);
    
    // Initialize charts object for this analysis
    biasCharts[analysisId] = {};
    
    // Create distribution visualizations
    if (distributionContainer && biasResults.attribute_distribution) {
        // Get attributes
        const attributes = Object.keys(biasResults.attribute_distribution);
        
        attributes.forEach(attr => {
            // Skip if there was an error
            if (biasResults.attribute_distribution[attr].error) return;
            
            // Create canvas
            const canvasId = `distribution-${analysisId}-${attr}`;
            const canvas = document.createElement('canvas');
            canvas.id = canvasId;
            
            // Create wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'chart-wrapper col';
            wrapper.appendChild(canvas);
            
            // Add to container
            distributionContainer.appendChild(wrapper);
            
            // Create chart
            const chartConfig = prepareBiasVisualization(biasResults, attr);
            if (chartConfig) {
                biasCharts[analysisId][canvasId] = createChart(canvasId, chartConfig);
            }
        });
    }
    
    // Create statistical parity visualizations
    if (parityContainer && biasResults.statistical_parity) {
        // Get attributes
        const attributes = Object.keys(biasResults.statistical_parity);
        
        attributes.forEach(attr => {
            // Skip if there was an error
            if (biasResults.statistical_parity[attr].error) return;
            
            // Create canvas
            const canvasId = `parity-${analysisId}-${attr}`;
            const canvas = document.createElement('canvas');
            canvas.id = canvasId;
            
            // Create wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'chart-wrapper col';
            wrapper.appendChild(canvas);
            
            // Add to container
            parityContainer.appendChild(wrapper);
            
            // Prepare chart data
            const parityData = biasResults.statistical_parity[attr];
            const labels = Object.keys(parityData.positive_rates);
            const values = Object.values(parityData.positive_rates);
            
            // Create chart
            const chartConfig = {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Positive Rate',
                        data: values,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgb(54, 162, 235)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: `Statistical Parity: ${attr}`
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.parsed.y || 0;
                                    return `Positive rate: ${(value * 100).toFixed(1)}%`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 1,
                            ticks: {
                                callback: function(value) {
                                    return (value * 100) + '%';
                                }
                            }
                        }
                    }
                }
            };
            
            biasCharts[analysisId][canvasId] = createChart(canvasId, chartConfig);
        });
    }
    
    // Create fairness metrics visualizations
    if (metricsContainer && fairnessMetrics && fairnessMetrics.metrics_by_attribute) {
        // Get attributes
        const attributes = Object.keys(fairnessMetrics.metrics_by_attribute);
        
        attributes.forEach(attr => {
            // Skip if there's no group metrics
            if (!fairnessMetrics.metrics_by_attribute[attr].group_metrics) return;
            
            // Create canvas
            const canvasId = `fairness-${analysisId}-${attr}`;
            const canvas = document.createElement('canvas');
            canvas.id = canvasId;
            
            // Create wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'chart-wrapper col';
            wrapper.appendChild(canvas);
            
            // Add to container
            metricsContainer.appendChild(wrapper);
            
            // Create chart
            const chartConfig = prepareFairnessVisualization(fairnessMetrics, attr);
            if (chartConfig) {
                biasCharts[analysisId][canvasId] = createChart(canvasId, chartConfig);
            }
        });
    }
}

/**
 * Populate bias analysis summary information
 * @param {string} analysisId - ID of the analysis
 * @param {Object} biasResults - Bias analysis results
 * @param {Object} fairnessMetrics - Fairness metrics results
 */
function populateBiasAnalysisSummary(analysisId, biasResults, fairnessMetrics) {
    const summaryContainer = document.getElementById(`bias-summary-${analysisId}`);
    if (!summaryContainer || !biasResults) return;
    
    // Create summary HTML
    let summaryHtml = '<h3>Bias Analysis Summary</h3>';
    
    // Overall assessment
    if (biasResults.overall_assessment) {
        summaryHtml += '<div class="mb-3"><h4>Risk Assessment</h4>';
        
        Object.keys(biasResults.overall_assessment).forEach(attr => {
            const assessment = biasResults.overall_assessment[attr];
            let riskClass = '';
            
            if (assessment.risk_level.includes('High')) {
                riskClass = 'high-risk';
            } else if (assessment.risk_level.includes('Medium')) {
                riskClass = 'medium-risk';
            } else {
                riskClass = 'low-risk';
            }
            
            summaryHtml += `
                <div class="assessment-box ${riskClass} mb-2">
                    <h5>${attr}: <span class="${riskClass}">${assessment.risk_level}</span></h5>
                    <p class="mb-1"><strong>Bias indicators:</strong></p>
                    <ul>
                        ${assessment.bias_indicators.length > 0 
                          ? assessment.bias_indicators.map(indicator => `<li>${indicator}</li>`).join('') 
                          : '<li>No significant bias indicators detected</li>'}
                    </ul>
                </div>
            `;
        });
        
        summaryHtml += '</div>';
    }
    
    // Statistical parity
    if (biasResults.statistical_parity) {
        summaryHtml += '<div class="mb-3"><h4>Statistical Parity</h4>';
        
        Object.keys(biasResults.statistical_parity).forEach(attr => {
            const parity = biasResults.statistical_parity[attr];
            
            // Skip if there was an error
            if (parity.error) {
                summaryHtml += `<p>Error analyzing ${attr}: ${parity.error}</p>`;
                return;
            }
            
            let parityClass = '';
            if (parity.assessment.includes('Good')) {
                parityClass = 'low-risk';
            } else if (parity.assessment.includes('Moderate')) {
                parityClass = 'medium-risk';
            } else {
                parityClass = 'high-risk';
            }
            
            summaryHtml += `
                <div class="bias-metric-card mb-2">
                    <h5>${attr}</h5>
                    <p><span class="metric-label">Parity Difference:</span> 
                       <span class="${parityClass}">${(parity.parity_difference * 100).toFixed(1)}%</span></p>
                    <p><span class="metric-label">Assessment:</span> 
                       <span class="${parityClass}">${parity.assessment}</span></p>
                </div>
            `;
        });
        
        summaryHtml += '</div>';
    }
    
    // Fairness metrics
    if (fairnessMetrics && fairnessMetrics.metrics_by_attribute) {
        summaryHtml += '<div class="mb-3"><h4>Fairness Metrics</h4>';
        
        Object.keys(fairnessMetrics.metrics_by_attribute).forEach(attr => {
            const metrics = fairnessMetrics.metrics_by_attribute[attr];
            
            // Skip if there's no group metrics
            if (!metrics.group_metrics) return;
            
            // Check for fairness assessment
            if (metrics.fairness_assessment) {
                let fairnessClass = '';
                if (metrics.fairness_assessment.includes('Good')) {
                    fairnessClass = 'low-risk';
                } else if (metrics.fairness_assessment.includes('Moderate')) {
                    fairnessClass = 'medium-risk';
                } else {
                    fairnessClass = 'high-risk';
                }
                
                summaryHtml += `
                    <div class="bias-metric-card mb-2">
                        <h5>${attr}</h5>
                        <p><span class="metric-label">Assessment:</span> 
                           <span class="${fairnessClass}">${metrics.fairness_assessment}</span></p>
                `;
                
                // Add disparities if available
                if (metrics.disparities) {
                    summaryHtml += '<p class="metric-label">Maximum disparities:</p><ul>';
                    
                    Object.keys(metrics.disparities).forEach(metricName => {
                        const disparity = metrics.disparities[metricName];
                        let disparityClass = '';
                        
                        if (disparity <= 0.05) {
                            disparityClass = 'low-risk';
                        } else if (disparity <= 0.1) {
                            disparityClass = 'medium-risk';
                        } else {
                            disparityClass = 'high-risk';
                        }
                        
                        const readableMetric = metricName
                            .replace(/_/g, ' ')
                            .replace(/\b\w/g, l => l.toUpperCase());
                        
                        summaryHtml += `
                            <li>${readableMetric}: 
                                <span class="${disparityClass}">${(disparity * 100).toFixed(1)}%</span>
                            </li>
                        `;
                    });
                    
                    summaryHtml += '</ul>';
                }
                
                summaryHtml += '</div>';
            }
        });
        
        summaryHtml += '</div>';
    }
    
    // Add recommendations
    summaryHtml += `
        <div class="mb-3">
            <h4>Recommendations</h4>
            <ul class="feature-list">
                ${generateBiasRecommendations(biasResults, fairnessMetrics)}
            </ul>
        </div>
    `;
    
    // Update the container
    summaryContainer.innerHTML = summaryHtml;
}

/**
 * Generate bias mitigation recommendations based on analysis results
 * @param {Object} biasResults - Bias analysis results
 * @param {Object} fairnessMetrics - Fairness metrics results
 * @returns {string} HTML string with recommendations
 */
function generateBiasRecommendations(biasResults, fairnessMetrics) {
    let recommendations = [];
    
    // Check for high-risk attributes
    if (biasResults.overall_assessment) {
        const highRiskAttrs = Object.keys(biasResults.overall_assessment).filter(attr => 
            biasResults.overall_assessment[attr].risk_level.includes('High')
        );
        
        if (highRiskAttrs.length > 0) {
            recommendations.push(`
                <li>Prioritize addressing bias in the high-risk attributes: 
                <strong>${highRiskAttrs.join(', ')}</strong></li>
            `);
        }
    }
    
    // Check for imbalanced distributions
    if (biasResults.attribute_distribution) {
        const imbalancedAttrs = Object.keys(biasResults.attribute_distribution).filter(attr => {
            const distribution = biasResults.attribute_distribution[attr];
            return distribution.assessment && 
                   (distribution.assessment.includes('Highly imbalanced') || 
                    distribution.assessment.includes('Moderately imbalanced'));
        });
        
        if (imbalancedAttrs.length > 0) {
            recommendations.push(`
                <li>Consider data rebalancing techniques for imbalanced attributes: 
                <strong>${imbalancedAttrs.join(', ')}</strong></li>
            `);
        }
    }
    
    // Check for statistical parity issues
    if (biasResults.statistical_parity) {
        const parityIssueAttrs = Object.keys(biasResults.statistical_parity).filter(attr => {
            const parity = biasResults.statistical_parity[attr];
            return parity.assessment && parity.assessment.includes('Poor');
        });
        
        if (parityIssueAttrs.length > 0) {
            recommendations.push(`
                <li>Implement post-processing techniques to improve statistical parity for: 
                <strong>${parityIssueAttrs.join(', ')}</strong></li>
            `);
        }
    }
    
    // Add general recommendations
    recommendations.push(`
        <li>Ensure your training data includes diverse and representative samples</li>
        <li>Consider using fairness-aware algorithms during model training</li>
        <li>Implement regular bias auditing for deployed models</li>
        <li>Review feature selection to remove potentially problematic proxies</li>
    `);
    
    return recommendations.join('');
}

/**
 * Analyze bias using API
 * @param {FormData} formData - Form data containing dataset and parameters
 * @returns {Promise} Promise resolving to bias analysis results
 */
function analyzeBiasAPI(formData) {
    return new Promise((resolve, reject) => {
        fetch('/api/analyze-bias/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                reject(new Error(data.error));
            } else {
                resolve(data);
            }
        })
        .catch(error => {
            reject(error);
        });
    });
}
