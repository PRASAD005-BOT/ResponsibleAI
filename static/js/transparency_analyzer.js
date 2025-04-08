/**
 * AI Ethics Platform - Transparency Analyzer
 * Handles functionality for model transparency analysis
 */

let transparencyCharts = {};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize transparency analyzer form
    const transparencyForm = document.getElementById('transparency-analyzer-form');
    if (transparencyForm) {
        initTransparencyForm();
    }
    
    // Initialize existing transparency analysis visualizations
    const transparencyAnalyses = document.querySelectorAll('.transparency-analysis');
    if (transparencyAnalyses.length > 0) {
        initExistingTransparencyVisualizations();
    }
});

/**
 * Initialize the transparency analyzer form
 */
function initTransparencyForm() {
    const form = document.getElementById('transparency-analyzer-form');
    const fileInput = document.getElementById('id_data_file');
    const fileLabel = document.querySelector('.file-input-label');
    const modelTypeSelect = document.getElementById('id_model_type');
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
    
    // Add model type change handler
    if (modelTypeSelect) {
        modelTypeSelect.addEventListener('change', updateFormFields);
        
        // Initialize on load
        updateFormFields();
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
    
    // Add CSV column analyzer
    initCSVColumnAnalyzer();
}

/**
 * Update form fields based on model type selection
 */
function updateFormFields() {
    const modelType = document.getElementById('id_model_type').value;
    const explanationLevelField = document.getElementById('id_explanation_level');
    
    // Adjust explanation level options based on model type
    if (explanationLevelField) {
        const advancedOption = explanationLevelField.querySelector('option[value="advanced"]');
        
        if (modelType === 'nlp' || modelType === 'computer_vision') {
            // Disable advanced option for complex models
            if (advancedOption) {
                advancedOption.disabled = true;
                
                // If advanced was selected, change to intermediate
                if (explanationLevelField.value === 'advanced') {
                    explanationLevelField.value = 'intermediate';
                }
            }
            
            // Add note about complex models
            const noteEl = document.getElementById('model-type-note');
            if (!noteEl) {
                const note = document.createElement('small');
                note.id = 'model-type-note';
                note.className = 'form-text text-warning';
                note.textContent = 'Note: Advanced explainability is limited for complex models like NLP and Computer Vision.';
                explanationLevelField.parentNode.appendChild(note);
            }
        } else {
            // Enable advanced option for other models
            if (advancedOption) {
                advancedOption.disabled = false;
            }
            
            // Remove note if it exists
            const noteEl = document.getElementById('model-type-note');
            if (noteEl) {
                noteEl.remove();
            }
        }
    }
}

/**
 * Initialize CSV column analyzer to help identify target column
 */
function initCSVColumnAnalyzer() {
    const fileInput = document.getElementById('id_data_file');
    const targetColumn = document.getElementById('id_target_column');
    
    if (!fileInput || !targetColumn) return;
    
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length === 0) return;
        
        const file = fileInput.files[0];
        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
            alert('Please select a CSV file');
            return;
        }
        
        // Read first few lines of CSV to extract headers
        const reader = new FileReader();
        reader.onload = function(e) {
            const contents = e.target.result;
            const lines = contents.split('\n');
            
            if (lines.length > 0) {
                // Parse headers (first line)
                const headers = parseCSVLine(lines[0]);
                
                if (headers.length > 0) {
                    // Create suggestions container
                    let suggestionsContainer = document.getElementById('column-suggestions');
                    if (!suggestionsContainer) {
                        suggestionsContainer = document.createElement('div');
                        suggestionsContainer.id = 'column-suggestions';
                        suggestionsContainer.className = 'column-suggestions mt-2';
                        targetColumn.parentNode.appendChild(suggestionsContainer);
                    }
                    
                    // Clear existing suggestions
                    suggestionsContainer.innerHTML = '';
                    
                    // Add heading
                    const heading = document.createElement('small');
                    heading.className = 'text-muted';
                    heading.textContent = 'Detected columns:';
                    suggestionsContainer.appendChild(heading);
                    
                    // Add column suggestions
                    headers.forEach(header => {
                        const badge = document.createElement('span');
                        badge.className = 'badge badge-info column-suggestion';
                        badge.textContent = header;
                        badge.style.cursor = 'pointer';
                        badge.addEventListener('click', function() {
                            targetColumn.value = header;
                        });
                        
                        suggestionsContainer.appendChild(badge);
                    });
                }
            }
        };
        
        // Read as text
        reader.readAsText(file);
    });
}

/**
 * Parse a CSV line into an array of values
 * @param {string} line - CSV line to parse
 * @returns {Array} Array of values
 */
function parseCSVLine(line) {
    const values = [];
    let inQuote = false;
    let currentValue = '';
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            inQuote = !inQuote;
        } else if (char === ',' && !inQuote) {
            values.push(currentValue.trim());
            currentValue = '';
        } else {
            currentValue += char;
        }
    }
    
    // Add the last value
    if (currentValue) {
        values.push(currentValue.trim());
    }
    
    return values;
}

/**
 * Helper function to decode HTML entities
 * Defined outside other functions to be globally available
 */
function decodeHtmlEntities(str) {
    if (!str) return '';
    const txt = document.createElement('textarea');
    txt.innerHTML = str;
    return txt.value;
}

/**
 * Initialize visualizations for existing transparency analyses
 */
function initExistingTransparencyVisualizations() {
    const transparencyAnalyses = document.querySelectorAll('.transparency-analysis');
    
    if (!transparencyAnalyses || transparencyAnalyses.length === 0) {
        console.log('No transparency analyses found on this page');
        return;
    }
    
    transparencyAnalyses.forEach(analysis => {
        try {
            // Get analysis data
            const analysisId = analysis.getAttribute('data-analysis-id');
            const transparencyResultsStr = analysis.getAttribute('data-transparency-results');
            
            if (!analysisId) {
                console.error('Missing analysis ID in transparency analysis element');
                return;
            }
            
            if (!transparencyResultsStr) {
                console.error(`Missing transparency results for analysis ID: ${analysisId}`);
                return;
            }
            
            // Parse JSON data safely
            let transparencyResults;
            
            try {
                // Decode HTML entities (like &quot;) before parsing
                const decodedResults = transparencyResultsStr ? decodeHtmlEntities(transparencyResultsStr) : '{}';
                transparencyResults = JSON.parse(decodedResults);
            } catch (parseError) {
                console.error('Error parsing transparency results JSON:', parseError);
                console.log('Raw JSON string:', transparencyResultsStr);
                transparencyResults = { error: 'Invalid JSON data' };
            }
            
            // Create visualizations
            if (transparencyResults && !transparencyResults.error) {
                createTransparencyVisualizations(analysisId, transparencyResults);
                
                // Show additional information
                populateTransparencySummary(analysisId, transparencyResults);
            }
            
        } catch (error) {
            console.error('Error initializing transparency visualization:', error);
        }
    });
}

/**
 * Create transparency analysis visualizations
 * @param {string} analysisId - ID of the analysis
 * @param {Object} transparencyResults - Transparency analysis results
 */
function createTransparencyVisualizations(analysisId, transparencyResults) {
    if (!transparencyResults || !analysisId) return;
    
    // Get visualization containers
    const featureContainer = document.getElementById(`feature-importance-${analysisId}`);
    const interactionContainer = document.getElementById(`feature-interactions-${analysisId}`);
    
    // Initialize charts object for this analysis
    transparencyCharts[analysisId] = {};
    
    // Create feature importance visualization
    if (featureContainer && transparencyResults.feature_importance) {
        // Create canvas
        const canvasId = `feature-importance-chart-${analysisId}`;
        const canvas = document.createElement('canvas');
        canvas.id = canvasId;
        
        // Add to container
        featureContainer.appendChild(canvas);
        
        // Create chart
        const chartConfig = prepareFeatureImportanceVisualization(transparencyResults);
        if (chartConfig) {
            try {
                if (typeof createChart === 'function') {
                    transparencyCharts[analysisId][canvasId] = createChart(canvasId, chartConfig);
                } else {
                    console.error('createChart function not available');
                }
            } catch (error) {
                console.error('Error creating feature importance chart:', error);
            }
        }
    }
    
    // Create feature interactions visualization
    if (interactionContainer && 
        transparencyResults.feature_interactions && 
        transparencyResults.feature_interactions.potential_interactions) {
        
        // Create canvas
        const canvasId = `feature-interactions-chart-${analysisId}`;
        const canvas = document.createElement('canvas');
        canvas.id = canvasId;
        
        // Add to container
        interactionContainer.appendChild(canvas);
        
        // Create chart
        const chartConfig = prepareFeatureInteractionsVisualization(transparencyResults);
        if (chartConfig) {
            try {
                if (typeof createChart === 'function') {
                    transparencyCharts[analysisId][canvasId] = createChart(canvasId, chartConfig);
                } else {
                    console.error('createChart function not available');
                }
            } catch (error) {
                console.error('Error creating feature interactions chart:', error);
            }
        }
    }
}

/**
 * Populate transparency analysis summary information
 * @param {string} analysisId - ID of the analysis
 * @param {Object} transparencyResults - Transparency analysis results
 */
function populateTransparencySummary(analysisId, transparencyResults) {
    const summaryContainer = document.getElementById(`transparency-summary-${analysisId}`);
    if (!summaryContainer || !transparencyResults) return;
    
    // Create summary HTML
    let summaryHtml = '<h3>Model Transparency Summary</h3>';
    
    // Model complexity
    if (transparencyResults.model_complexity) {
        const complexity = transparencyResults.model_complexity;
        
        summaryHtml += `
            <div class="mb-3">
                <h4>Model Complexity</h4>
                <div class="bias-metric-card">
                    <p><span class="metric-label">Complexity Level:</span> 
                       <span class="metric-value">${complexity.complexity_level}</span></p>
                    <p><span class="metric-label">Feature Count:</span> 
                       <span class="metric-value">${complexity.feature_count.total}</span> 
                       (${complexity.feature_count.numerical} numerical, 
                       ${complexity.feature_count.categorical} categorical)</p>
                    <p><span class="metric-label">Interpretability Potential:</span> 
                       <span class="metric-value">${complexity.interpretability_potential}</span></p>
                    
                    <div class="mt-2">
                        <p class="metric-label">Recommended Interpretable Models:</p>
                        <ul>
                            ${complexity.recommended_interpretable_models.map(model => 
                                `<li>${model}</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Feature importance
    if (transparencyResults.feature_importance && 
        transparencyResults.feature_importance.top_features) {
        
        const topFeatures = transparencyResults.feature_importance.top_features;
        
        summaryHtml += `
            <div class="mb-3">
                <h4>Key Features</h4>
                <div class="bias-metric-card">
                    <p class="metric-label">Top 5 most influential features:</p>
                    <ol>
                        ${topFeatures.map(feature => 
                            `<li><strong>${feature}</strong></li>`
                        ).join('')}
                    </ol>
                </div>
            </div>
        `;
    }
    
    // Model limitations
    if (transparencyResults.model_limitations) {
        summaryHtml += `
            <div class="mb-3">
                <h4>Model Limitations</h4>
                <div class="bias-metric-card">
                    <p class="metric-label">Potential limitations of this model:</p>
                    <ul>
                        ${transparencyResults.model_limitations.map(limitation => 
                            `<li>${limitation}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    // Recommended explainability methods
    if (transparencyResults.recommended_explainability_methods) {
        summaryHtml += `
            <div class="mb-3">
                <h4>Recommended Explainability Methods</h4>
                <div class="bias-metric-card">
                    <ul>
                        ${transparencyResults.recommended_explainability_methods.map(method => 
                            `<li>${method}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    // Add recommendations
    summaryHtml += `
        <div class="mb-3">
            <h4>Transparency Recommendations</h4>
            <ul class="feature-list">
                ${generateTransparencyRecommendations(transparencyResults)}
            </ul>
        </div>
    `;
    
    // Update the container
    summaryContainer.innerHTML = summaryHtml;
}

/**
 * Generate model transparency recommendations based on analysis results
 * @param {Object} transparencyResults - Transparency analysis results
 * @returns {string} HTML string with recommendations
 */
function generateTransparencyRecommendations(transparencyResults) {
    let recommendations = [];
    
    // Check model complexity
    if (transparencyResults.model_complexity) {
        const complexity = transparencyResults.model_complexity.complexity_level;
        
        if (complexity === 'High') {
            recommendations.push(`
                <li>Consider using simpler models for better interpretability, or implement 
                post-hoc explanation methods like SHAP or LIME</li>
                <li>Break down complex models into smaller, more interpretable components</li>
            `);
        } else if (complexity === 'Medium') {
            recommendations.push(`
                <li>Focus on explaining the most important features identified in the analysis</li>
                <li>Consider using inherently interpretable models like decision trees for critical decisions</li>
            `);
        } else {
            recommendations.push(`
                <li>Your model has good interpretability potential - use simple visualization techniques 
                to explain decisions</li>
            `);
        }
    }
    
    // Check feature importance
    if (transparencyResults.feature_importance) {
        const importanceCategories = transparencyResults.feature_importance.importance_categories;
        
        if (importanceCategories && importanceCategories.high_importance) {
            if (importanceCategories.high_importance.length <= 3) {
                recommendations.push(`
                    <li>Your model depends heavily on a small number of features. Create focused 
                    explanations around ${importanceCategories.high_importance.join(', ')}</li>
                `);
            }
        }
    }
    
    // Check feature interactions
    if (transparencyResults.feature_interactions && 
        transparencyResults.feature_interactions.recommendation) {
        
        recommendations.push(`
            <li>${transparencyResults.feature_interactions.recommendation}</li>
        `);
    }
    
    // Add general recommendations
    recommendations.push(`
        <li>Document model decisions with explanation dashboards for stakeholders</li>
        <li>Implement "what-if" analysis tools to help users understand how changes affect predictions</li>
        <li>Create plain-language explanations for non-technical stakeholders</li>
        <li>Establish a feedback mechanism for users to flag confusing or unexpected model behavior</li>
    `);
    
    return recommendations.join('');
}

/**
 * Analyze model transparency using API
 * @param {FormData} formData - Form data containing dataset and parameters
 * @returns {Promise} Promise resolving to transparency analysis results
 */
function analyzeTransparencyAPI(formData) {
    return new Promise((resolve, reject) => {
        fetch('/api/analyze-model-transparency/', {
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
