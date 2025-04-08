/**
 * AI Ethics Platform - Governance Framework JavaScript
 * Handles governance framework display and interaction
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize framework buttons
    initFrameworkButtons();
    
    // Initialize template buttons
    initTemplateButtons();
    
    // Close modal event handlers
    const closeModalBtn = document.getElementById('close-modal-btn');
    const closePreviewBtn = document.getElementById('close-preview-btn');
    const modal = document.getElementById('template-preview-modal');
    
    if (closeModalBtn && modal) {
        closeModalBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    if (closePreviewBtn && modal) {
        closePreviewBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside the modal content
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Download templates button
    const downloadAllBtn = document.getElementById('download-all-btn');
    if (downloadAllBtn) {
        downloadAllBtn.addEventListener('click', function() {
            alert('This feature will be available soon. Please check back later.');
        });
    }
    
    const downloadTemplateBtn = document.getElementById('download-template-btn');
    if (downloadTemplateBtn) {
        downloadTemplateBtn.addEventListener('click', function() {
            alert('This feature will be available soon. Please check back later.');
        });
    }
});

/**
 * Initialize framework view buttons
 */
function initFrameworkButtons() {
    const frameworkButtons = document.querySelectorAll('.view-framework-btn');
    
    frameworkButtons.forEach(button => {
        button.addEventListener('click', function() {
            const frameworkType = this.getAttribute('data-framework');
            toggleFrameworkDetails(frameworkType);
            loadFrameworkDetails(frameworkType);
        });
    });
}

/**
 * Toggle framework details section
 * @param {string} frameworkType - Type of framework
 */
function toggleFrameworkDetails(frameworkType) {
    const detailsSection = document.getElementById(`${frameworkType}-framework-details`);
    
    // Close all other framework details
    const allDetails = document.querySelectorAll('.framework-details');
    allDetails.forEach(details => {
        if (details.id !== `${frameworkType}-framework-details`) {
            details.classList.remove('open');
        }
    });
    
    // Toggle this framework details
    if (detailsSection) {
        detailsSection.classList.toggle('open');
        
        // Scroll to framework details if opening
        if (detailsSection.classList.contains('open')) {
            setTimeout(() => {
                detailsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    }
}

/**
 * Load framework details from API
 * @param {string} frameworkType - Type of framework
 */
function loadFrameworkDetails(frameworkType) {
    const contentContainer = document.getElementById(`${frameworkType}-framework-content`);
    
    if (!contentContainer) return;
    
    // Show loading state
    contentContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner"></div>
            <p>Loading framework details...</p>
        </div>
    `;
    
    // Fetch framework details
    fetch(`/api/get-governance-framework/${frameworkType}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                showFrameworkError(contentContainer, data.error);
            } else if (data.success && data.framework) {
                displayFramework(contentContainer, data.framework);
            } else {
                showFrameworkError(contentContainer, 'Invalid response from server');
            }
        })
        .catch(error => {
            showFrameworkError(contentContainer, error.message);
        });
}

/**
 * Display framework content
 * @param {HTMLElement} container - Container element
 * @param {Object} framework - Framework data
 */
function displayFramework(container, framework) {
    let html = `
        <h3>${framework.title}</h3>
        <p>${framework.description}</p>
        <p><strong>Version:</strong> ${framework.version}</p>
    `;
    
    // Components section
    if (framework.components && framework.components.length > 0) {
        html += '<h4>Framework Components</h4>';
        
        framework.components.forEach(component => {
            html += `
                <div class="component-card card mb-3">
                    <div class="card-body">
                        <h5>${component.name}</h5>
                        <p>${component.description}</p>
                    `;
            
            if (component.key_elements && component.key_elements.length > 0) {
                html += '<div class="mt-3">';
                
                component.key_elements.forEach(element => {
                    html += `
                        <div class="mb-2">
                            <h6>${element.name}</h6>
                            <p>${element.description}</p>
                    `;
                    
                    if (element.implementation_steps && element.implementation_steps.length > 0) {
                        html += '<ul>';
                        element.implementation_steps.forEach(step => {
                            html += `<li>${step}</li>`;
                        });
                        html += '</ul>';
                    }
                    
                    html += '</div>';
                });
                
                html += '</div>';
            }
            
            html += `
                    </div>
                </div>
            `;
        });
    }
    
    // Implementation roadmap
    if (framework.implementation_roadmap) {
        html += '<h4>Implementation Roadmap</h4>';
        
        for (const phase in framework.implementation_roadmap) {
            const phaseData = framework.implementation_roadmap[phase];
            
            html += `
                <div class="phase-card">
                    <h5>${phaseData.name}</h5>
                    <p><strong>Timeframe:</strong> ${phaseData.timeframe}</p>
                    <p><strong>Key Activities:</strong></p>
                    <ul>
            `;
            
            phaseData.key_activities.forEach(activity => {
                html += `<li>${activity}</li>`;
            });
            
            html += `
                    </ul>
                </div>
            `;
        }
    }
    
    // Industry-specific
    if (framework.industries && framework.industries.length > 0) {
        html += '<h4>Industry-Specific Considerations</h4>';
        
        framework.industries.forEach(industry => {
            html += `
                <div class="component-card card mb-3">
                    <div class="card-body">
                        <h5>${industry.name}</h5>
                        
                        <p><strong>Unique Considerations:</strong></p>
                        <ul>
            `;
            
            industry.unique_considerations.forEach(consideration => {
                html += `<li>${consideration}</li>`;
            });
            
            html += `
                        </ul>
                        
                        <div class="mt-3">
                            <p><strong>Key Governance Elements:</strong></p>
            `;
            
            industry.key_governance_elements.forEach(element => {
                html += `
                    <div class="mb-2">
                        <h6>${element.name}</h6>
                        <p>${element.description}</p>
                `;
                
                if (element.implementation_steps && element.implementation_steps.length > 0) {
                    html += '<ul>';
                    element.implementation_steps.forEach(step => {
                        html += `<li>${step}</li>`;
                    });
                    html += '</ul>';
                }
                
                html += '</div>';
            });
            
            html += `
                        </div>
                    </div>
                </div>
            `;
        });
    }
    
    // Regulatory alignment
    if (framework.regulatory_alignment) {
        html += `
            <h4>Regulatory Alignment</h4>
            <p>${framework.regulatory_alignment.name}</p>
        `;
        
        if (framework.regulatory_alignment.key_regulations && framework.regulatory_alignment.key_regulations.length > 0) {
            html += '<div class="mt-3">';
            
            framework.regulatory_alignment.key_regulations.forEach(regulation => {
                html += `
                    <div class="mb-3">
                        <h6>${regulation.regulation}</h6>
                        <p><strong>Key Requirements:</strong></p>
                        <ul>
                `;
                
                regulation.key_requirements.forEach(requirement => {
                    html += `<li>${requirement}</li>`;
                });
                
                html += `
                        </ul>
                    </div>
                `;
            });
            
            html += '</div>';
        }
    }
    
    container.innerHTML = html;
}

/**
 * Show error message when framework loading fails
 * @param {HTMLElement} container - Container element
 * @param {string} message - Error message
 */
function showFrameworkError(container, message) {
    container.innerHTML = `
        <div class="alert alert-error">
            <p><strong>Error loading framework:</strong> ${message}</p>
            <p>Please try again later or contact support if the problem persists.</p>
        </div>
    `;
}

/**
 * Initialize template preview buttons
 */
function initTemplateButtons() {
    const templateButtons = document.querySelectorAll('.template-btn');
    const modal = document.getElementById('template-preview-modal');
    const modalTitle = document.getElementById('modal-title');
    const templateContent = document.getElementById('template-content');
    
    templateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const templateType = this.getAttribute('data-template');
            
            // Set modal title based on template type
            if (modalTitle) {
                if (templateType === 'impact-assessment') {
                    modalTitle.textContent = 'AI Impact Assessment Template';
                } else if (templateType === 'ethics-review') {
                    modalTitle.textContent = 'AI Ethics Review Checklist';
                } else if (templateType === 'model-documentation') {
                    modalTitle.textContent = 'Model Documentation Template';
                } else {
                    modalTitle.textContent = 'Template Preview';
                }
            }
            
            // Load template content
            if (templateContent) {
                templateContent.innerHTML = `
                    <div class="text-center">
                        <div class="spinner"></div>
                        <p>Loading template...</p>
                    </div>
                `;
                
                // Simulate loading template (in a real app, this would fetch from server)
                setTimeout(() => {
                    if (templateType === 'impact-assessment') {
                        displayImpactAssessmentTemplate(templateContent);
                    } else if (templateType === 'ethics-review') {
                        displayEthicsReviewTemplate(templateContent);
                    } else if (templateType === 'model-documentation') {
                        displayModelDocumentationTemplate(templateContent);
                    } else {
                        templateContent.innerHTML = `
                            <div class="alert alert-error">
                                <p>Unknown template type: ${templateType}</p>
                            </div>
                        `;
                    }
                }, 500);
            }
            
            // Show modal
            if (modal) {
                modal.style.display = 'block';
            }
        });
    });
}

/**
 * Display impact assessment template
 * @param {HTMLElement} container - Container element
 */
function displayImpactAssessmentTemplate(container) {
    container.innerHTML = `
        <h4>AI Impact Assessment</h4>
        
        <div class="mb-3">
            <p><strong>Purpose:</strong> This template helps assess the potential ethical impacts of AI systems before development or deployment.</p>
        </div>
        
        <form>
            <div class="form-group">
                <label class="form-label">Project Name</label>
                <input type="text" class="form-control" placeholder="Enter project name">
            </div>
            
            <div class="form-group">
                <label class="form-label">Project Description</label>
                <textarea class="form-control" rows="3" placeholder="Describe the AI system/project"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Intended Use</label>
                <textarea class="form-control" rows="2" placeholder="Describe the intended use and context"></textarea>
            </div>
            
            <h5 class="mt-4">Risk Assessment</h5>
            
            <div class="form-group">
                <label class="form-label">Fairness & Bias Risks</label>
                <textarea class="form-control" rows="2" placeholder="Identify potential fairness and bias risks"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Privacy Risks</label>
                <textarea class="form-control" rows="2" placeholder="Identify potential privacy risks"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Security Risks</label>
                <textarea class="form-control" rows="2" placeholder="Identify potential security risks"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Transparency Risks</label>
                <textarea class="form-control" rows="2" placeholder="Identify potential transparency risks"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Societal & Environmental Impacts</label>
                <textarea class="form-control" rows="2" placeholder="Identify potential broader impacts"></textarea>
            </div>
            
            <h5 class="mt-4">Mitigation Planning</h5>
            
            <div class="form-group">
                <label class="form-label">Fairness & Bias Mitigation</label>
                <textarea class="form-control" rows="2" placeholder="Describe planned mitigation strategies"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Privacy Protection Measures</label>
                <textarea class="form-control" rows="2" placeholder="Describe planned protection measures"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Monitoring & Evaluation Plan</label>
                <textarea class="form-control" rows="2" placeholder="Describe how the system will be monitored"></textarea>
            </div>
            
            <h5 class="mt-4">Stakeholder Analysis</h5>
            
            <div class="form-group">
                <label class="form-label">Affected Stakeholders</label>
                <textarea class="form-control" rows="2" placeholder="Identify all stakeholders who may be affected"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Stakeholder Engagement Plan</label>
                <textarea class="form-control" rows="2" placeholder="Describe how stakeholders will be engaged"></textarea>
            </div>
            
            <h5 class="mt-4">Review & Approval</h5>
            
            <div class="form-group">
                <label class="form-label">Assessment Completed By</label>
                <input type="text" class="form-control" placeholder="Enter name and role">
            </div>
            
            <div class="form-group">
                <label class="form-label">Date</label>
                <input type="date" class="form-control">
            </div>
            
            <div class="form-group">
                <label class="form-label">Approver</label>
                <input type="text" class="form-control" placeholder="Enter name and role">
            </div>
        </form>
    `;
}

/**
 * Display ethics review template
 * @param {HTMLElement} container - Container element
 */
function displayEthicsReviewTemplate(container) {
    container.innerHTML = `
        <h4>AI Ethics Review Checklist</h4>
        
        <div class="mb-3">
            <p><strong>Purpose:</strong> Use this checklist to evaluate AI systems against ethical standards.</p>
        </div>
        
        <form>
            <h5>1. Fairness & Non-discrimination</h5>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Data used for training has been analyzed for potential biases
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> System has been tested for performance disparities across demographic groups
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Fairness metrics have been defined and measured
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Bias mitigation strategies have been implemented where necessary
                </label>
            </div>
            
            <h5 class="mt-4">2. Transparency & Explainability</h5>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> System's purpose and capabilities are clearly documented
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Decision-making process can be explained in understandable terms
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Important features/factors influencing decisions are identifiable
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Limitations and error rates are documented and communicated
                </label>
            </div>
            
            <h5 class="mt-4">3. Privacy & Data Governance</h5>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Data collection and usage comply with relevant privacy regulations
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Data minimization principles have been applied
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Appropriate consent has been obtained for data usage
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Privacy-enhancing technologies have been considered
                </label>
            </div>
            
            <h5 class="mt-4">4. Security & Safety</h5>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> System has been tested for potential security vulnerabilities
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Safeguards are in place to prevent unauthorized access or manipulation
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> System robustness has been tested under various conditions
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Human oversight mechanisms exist for critical decisions
                </label>
            </div>
            
            <h5 class="mt-4">5. Accountability & Governance</h5>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Clear roles and responsibilities have been defined
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Documentation exists for design decisions and trade-offs
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Monitoring and evaluation processes are in place
                </label>
            </div>
            
            <div class="form-group">
                <label class="form-label">
                    <input type="checkbox"> Mechanisms exist for addressing issues and complaints
                </label>
            </div>
            
            <h5 class="mt-4">Review Summary</h5>
            
            <div class="form-group">
                <label class="form-label">Areas of Concern</label>
                <textarea class="form-control" rows="3" placeholder="List any ethical concerns identified"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Recommended Actions</label>
                <textarea class="form-control" rows="3" placeholder="List recommended actions to address concerns"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Reviewed By</label>
                <input type="text" class="form-control" placeholder="Enter name and role">
            </div>
            
            <div class="form-group">
                <label class="form-label">Review Date</label>
                <input type="date" class="form-control">
            </div>
        </form>
    `;
}

/**
 * Display model documentation template
 * @param {HTMLElement} container - Container element
 */
function displayModelDocumentationTemplate(container) {
    container.innerHTML = `
        <h4>Model Documentation Template</h4>
        
        <div class="mb-3">
            <p><strong>Purpose:</strong> This template helps document AI models according to governance standards.</p>
        </div>
        
        <form>
            <h5>Model Overview</h5>
            
            <div class="form-group">
                <label class="form-label">Model Name</label>
                <input type="text" class="form-control" placeholder="Enter model name">
            </div>
            
            <div class="form-group">
                <label class="form-label">Version</label>
                <input type="text" class="form-control" placeholder="Enter version number">
            </div>
            
            <div class="form-group">
                <label class="form-label">Model Type</label>
                <select class="form-control">
                    <option>Classification</option>
                    <option>Regression</option>
                    <option>Clustering</option>
                    <option>Natural Language Processing</option>
                    <option>Computer Vision</option>
                    <option>Reinforcement Learning</option>
                    <option>Other</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Purpose & Intended Use</label>
                <textarea class="form-control" rows="3" placeholder="Describe what the model is designed to do and its intended use cases"></textarea>
            </div>
            
            <h5 class="mt-4">Model Development</h5>
            
            <div class="form-group">
                <label class="form-label">Development Team</label>
                <input type="text" class="form-control" placeholder="Enter names and roles">
            </div>
            
            <div class="form-group">
                <label class="form-label">Development Timeline</label>
                <input type="text" class="form-control" placeholder="Enter development period">
            </div>
            
            <div class="form-group">
                <label class="form-label">Algorithm(s) Used</label>
                <input type="text" class="form-control" placeholder="Enter algorithms used">
            </div>
            
            <div class="form-group">
                <label class="form-label">Key Hyperparameters</label>
                <textarea class="form-control" rows="2" placeholder="List important hyperparameters and their values"></textarea>
            </div>
            
            <h5 class="mt-4">Data</h5>
            
            <div class="form-group">
                <label class="form-label">Training Data Description</label>
                <textarea class="form-control" rows="3" placeholder="Describe the data used to train the model"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Data Source(s)</label>
                <input type="text" class="form-control" placeholder="Enter data sources">
            </div>
            
            <div class="form-group">
                <label class="form-label">Data Preprocessing Steps</label>
                <textarea class="form-control" rows="3" placeholder="Describe preprocessing steps applied to the data"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Data Limitations & Biases</label>
                <textarea class="form-control" rows="3" placeholder="Describe any known limitations or biases in the data"></textarea>
            </div>
            
            <h5 class="mt-4">Performance & Evaluation</h5>
            
            <div class="form-group">
                <label class="form-label">Performance Metrics</label>
                <textarea class="form-control" rows="2" placeholder="List metrics used to evaluate performance and their values"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Validation Method</label>
                <input type="text" class="form-control" placeholder="Describe validation approach (e.g., cross-validation)">
            </div>
            
            <div class="form-group">
                <label class="form-label">Fairness Evaluation</label>
                <textarea class="form-control" rows="2" placeholder="Describe fairness metrics and results"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Known Limitations</label>
                <textarea class="form-control" rows="2" placeholder="Describe known limitations of the model"></textarea>
            </div>
            
            <h5 class="mt-4">Deployment & Maintenance</h5>
            
            <div class="form-group">
                <label class="form-label">Deployment Environment</label>
                <input type="text" class="form-control" placeholder="Describe where the model is deployed">
            </div>
            
            <div class="form-group">
                <label class="form-label">Monitoring Plan</label>
                <textarea class="form-control" rows="2" placeholder="Describe how the model will be monitored"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Update Process</label>
                <textarea class="form-control" rows="2" placeholder="Describe the process for updating the model"></textarea>
            </div>
            
            <div class="form-group">
                <label class="form-label">Ethical Considerations</label>
                <textarea class="form-control" rows="3" placeholder="Describe ethical considerations and mitigations"></textarea>
            </div>
            
            <h5 class="mt-4">Approvals</h5>
            
            <div class="form-group">
                <label class="form-label">Documentation Completed By</label>
                <input type="text" class="form-control" placeholder="Enter name and role">
            </div>
            
            <div class="form-group">
                <label class="form-label">Date</label>
                <input type="date" class="form-control">
            </div>
            
            <div class="form-group">
                <label class="form-label">Approved By</label>
                <input type="text" class="form-control" placeholder="Enter name and role">
            </div>
        </form>
    `;
}
