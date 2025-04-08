/**
 * AI Ethics Platform - Chart Utilities
 * Contains helper functions for creating and managing charts
 */

/**
 * Creates a Chart.js instance with the provided configuration
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} chartConfig - Chart.js configuration object
 * @returns {Chart} Chart instance
 */
function createChart(canvasId, chartConfig) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element with ID ${canvasId} not found`);
        return null;
    }
    
    // Create and return new chart
    return new Chart(canvas.getContext('2d'), chartConfig);
}

/**
 * Updates an existing chart with new data
 * @param {Chart} chart - Chart.js instance
 * @param {Array} labels - New labels array
 * @param {Array} datasets - New datasets array
 */
function updateChart(chart, labels, datasets) {
    if (!chart) {
        console.error('No chart provided to update');
        return;
    }
    
    chart.data.labels = labels;
    chart.data.datasets = datasets;
    chart.update();
}

/**
 * Generates a palette of colors for charts
 * @param {number} count - Number of colors to generate
 * @param {number} opacity - Opacity value (0-1)
 * @returns {Array} Array of color strings
 */
function generateChartColors(count, opacity = 0.7) {
    const baseColors = [
        [255, 99, 132],   // red
        [54, 162, 235],   // blue
        [255, 206, 86],   // yellow
        [75, 192, 192],   // green
        [153, 102, 255],  // purple
        [255, 159, 64],   // orange
        [199, 199, 199],  // grey
        [83, 102, 255],   // indigo
        [40, 159, 94],    // teal
        [210, 99, 132]    // pink
    ];
    
    const colors = [];
    
    for (let i = 0; i < count; i++) {
        const colorIndex = i % baseColors.length;
        const [r, g, b] = baseColors[colorIndex];
        colors.push(`rgba(${r}, ${g}, ${b}, ${opacity})`);
    }
    
    return colors;
}

/**
 * Creates a color scale based on values (red to green)
 * @param {number} value - Value between 0 and 1
 * @param {number} opacity - Opacity value (0-1)
 * @returns {string} RGBA color string
 */
function getColorScale(value, opacity = 0.7) {
    // Ensure value is between 0 and 1
    const normalizedValue = Math.max(0, Math.min(1, value));
    
    // Calculate RGB values for a red-to-green gradient
    const r = Math.round(255 * (1 - normalizedValue));
    const g = Math.round(255 * normalizedValue);
    const b = 0;
    
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

/**
 * Prepares bias visualization data for Chart.js
 * @param {Object} biasResults - Bias analysis results
 * @param {string} attributeName - Name of attribute to visualize
 * @returns {Object} Chart.js configuration
 */
function prepareBiasVisualization(biasResults, attributeName) {
    // Check if we have distribution data for this attribute
    if (!biasResults.attribute_distribution || 
        !biasResults.attribute_distribution[attributeName] ||
        !biasResults.attribute_distribution[attributeName].distribution) {
        return null;
    }
    
    const distribution = biasResults.attribute_distribution[attributeName].distribution;
    const labels = Object.keys(distribution);
    const values = Object.values(distribution);
    
    // Generate colors
    const colors = generateChartColors(labels.length);
    
    return {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace(/, [\d\.]+\)/, ', 1)')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: `Distribution of ${attributeName}`
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return `${label}: ${(value * 100).toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    };
}

/**
 * Prepares fairness metrics visualization for Chart.js
 * @param {Object} fairnessMetrics - Fairness metrics results
 * @param {string} attributeName - Name of attribute to visualize
 * @returns {Object} Chart.js configuration
 */
function prepareFairnessVisualization(fairnessMetrics, attributeName) {
    // Check if we have metrics for this attribute
    if (!fairnessMetrics.metrics_by_attribute || 
        !fairnessMetrics.metrics_by_attribute[attributeName] ||
        !fairnessMetrics.metrics_by_attribute[attributeName].group_metrics) {
        return null;
    }
    
    const groupMetrics = fairnessMetrics.metrics_by_attribute[attributeName].group_metrics;
    const groups = Object.keys(groupMetrics);
    
    // Extract performance metrics
    const truePositiveRates = [];
    const falsePositiveRates = [];
    const accuracies = [];
    
    groups.forEach(group => {
        if (groupMetrics[group].error) {
            return;
        }
        
        truePositiveRates.push({
            group: group,
            value: groupMetrics[group].true_positive_rate || 0
        });
        
        falsePositiveRates.push({
            group: group,
            value: groupMetrics[group].false_positive_rate || 0
        });
        
        accuracies.push({
            group: group,
            value: groupMetrics[group].accuracy || 0
        });
    });
    
    // Prepare chart data
    const labels = groups;
    const datasets = [
        {
            label: 'True Positive Rate',
            data: groups.map(group => {
                return groupMetrics[group].error ? null : (groupMetrics[group].true_positive_rate || 0);
            }),
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            borderColor: 'rgb(75, 192, 192)',
            borderWidth: 1
        },
        {
            label: 'False Positive Rate',
            data: groups.map(group => {
                return groupMetrics[group].error ? null : (groupMetrics[group].false_positive_rate || 0);
            }),
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgb(255, 99, 132)',
            borderWidth: 1
        },
        {
            label: 'Accuracy',
            data: groups.map(group => {
                return groupMetrics[group].error ? null : (groupMetrics[group].accuracy || 0);
            }),
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgb(54, 162, 235)',
            borderWidth: 1
        }
    ];
    
    return {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: `Fairness Metrics by ${attributeName}`
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const datasetLabel = context.dataset.label || '';
                            const value = context.parsed.y || 0;
                            return `${datasetLabel}: ${(value * 100).toFixed(1)}%`;
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
}

/**
 * Prepares feature importance visualization for Chart.js
 * @param {Object} transparencyResults - Transparency analysis results
 * @returns {Object} Chart.js configuration
 */
function prepareFeatureImportanceVisualization(transparencyResults) {
    // Check if we have feature importance data
    if (!transparencyResults.feature_importance || 
        !transparencyResults.feature_importance.feature_importance_scores) {
        return null;
    }
    
    const featureScores = transparencyResults.feature_importance.feature_importance_scores;
    const features = Object.keys(featureScores);
    const scores = Object.values(featureScores);
    
    // Sort features by importance
    const sortedIndices = scores
        .map((score, index) => ({ score, index }))
        .sort((a, b) => b.score - a.score)
        .map(item => item.index);
    
    const sortedFeatures = sortedIndices.map(index => features[index]);
    const sortedScores = sortedIndices.map(index => scores[index]);
    
    // Limit to top 10 features
    const topFeatures = sortedFeatures.slice(0, 10);
    const topScores = sortedScores.slice(0, 10);
    
    // Generate colors based on importance
    const colors = topScores.map(score => getColorScale(score));
    
    return {
        type: 'bar',
        data: {
            labels: topFeatures,
            datasets: [{
                label: 'Feature Importance',
                data: topScores,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace(/, [\d\.]+\)/, ', 1)')),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Feature Importance'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.x || 0;
                            return `Importance: ${value.toFixed(3)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    };
}

/**
 * Prepares feature interactions visualization for Chart.js
 * @param {Object} transparencyResults - Transparency analysis results
 * @returns {Object} Chart.js configuration
 */
function prepareFeatureInteractionsVisualization(transparencyResults) {
    // Check if we have feature interactions data
    if (!transparencyResults.feature_interactions || 
        !transparencyResults.feature_interactions.potential_interactions) {
        return null;
    }
    
    const interactions = transparencyResults.feature_interactions.potential_interactions;
    
    // Create labels and values
    const labels = interactions.map(item => item.features.join(' × '));
    const values = interactions.map(item => item.strength);
    
    // Generate colors
    const colors = generateChartColors(labels.length);
    
    return {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Interaction Strength',
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace(/, [\d\.]+\)/, ', 1)')),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Feature Interactions'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.x || 0;
                            return `Strength: ${value.toFixed(3)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    };
}
