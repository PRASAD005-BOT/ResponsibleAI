/**
 * AI Ethics Platform - Case Studies JavaScript
 * Handles case studies display and interaction
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize case study filters
    initCaseStudyFilters();
    
    // Initialize view case study buttons
    initViewCaseStudyButtons();
});

/**
 * Initialize case study filter buttons
 */
function initCaseStudyFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const caseStudyCards = document.querySelectorAll('.case-study-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get filter value
            const filter = this.getAttribute('data-filter');
            
            // Update active button
            filterButtons.forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            // Filter case studies
            caseStudyCards.forEach(card => {
                if (filter === 'all' || card.getAttribute('data-category') === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

/**
 * Initialize view case study buttons
 */
function initViewCaseStudyButtons() {
    const viewButtons = document.querySelectorAll('.view-case-study-btn');
    
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get case study ID
            const caseId = this.getAttribute('data-case-id');
            const contentEl = document.getElementById(`case-study-${caseId}`);
            
            if (contentEl) {
                // Toggle content visibility
                if (contentEl.style.display === 'none' || !contentEl.style.display) {
                    // Hide all other open case studies
                    document.querySelectorAll('.case-study-content').forEach(content => {
                        if (content.id !== `case-study-${caseId}` && content.style.display !== 'none') {
                            content.style.display = 'none';
                            
                            // Update button text for other case studies
                            const otherCaseId = content.id.replace('case-study-', '');
                            const otherButton = document.querySelector(`.view-case-study-btn[data-case-id="${otherCaseId}"]`);
                            if (otherButton) {
                                otherButton.textContent = 'View Full Case Study';
                            }
                        }
                    });
                    
                    // Show this case study
                    contentEl.style.display = 'block';
                    this.textContent = 'Hide Case Study';
                    
                    // Track case study view (for analytics)
                    trackCaseStudyView(caseId);
                    
                    // Scroll to content
                    setTimeout(() => {
                        contentEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                } else {
                    contentEl.style.display = 'none';
                    this.textContent = 'View Full Case Study';
                }
            }
        });
    });
}

/**
 * Track case study view for analytics
 * @param {string} caseId - Case study ID
 */
function trackCaseStudyView(caseId) {
    // This would send analytics data to the server
    // For now, we'll just log to console
    console.log(`Case study viewed: ID ${caseId}`);
}

/**
 * Generate a related case studies list based on category
 * @param {string} category - Case study category
 * @param {string} currentCaseId - Current case study ID to exclude
 * @returns {Array} Array of related case study IDs
 */
function getRelatedCaseStudies(category, currentCaseId) {
    // Get all case studies with the same category
    const relatedCases = [];
    const caseStudyCards = document.querySelectorAll(`.case-study-card[data-category="${category}"]`);
    
    caseStudyCards.forEach(card => {
        const viewButton = card.querySelector('.view-case-study-btn');
        if (viewButton) {
            const caseId = viewButton.getAttribute('data-case-id');
            if (caseId !== currentCaseId) {
                relatedCases.push(caseId);
            }
        }
    });
    
    return relatedCases;
}

/**
 * Show related case studies for a given case
 * @param {string} caseId - Case study ID
 * @param {string} category - Case study category
 */
function showRelatedCaseStudies(caseId, category) {
    const relatedCases = getRelatedCaseStudies(category, caseId);
    const contentEl = document.getElementById(`case-study-${caseId}`);
    
    if (contentEl && relatedCases.length > 0) {
        // Check if related cases section already exists
        let relatedSection = contentEl.querySelector('.related-cases');
        
        if (!relatedSection) {
            // Create related cases section
            relatedSection = document.createElement('div');
            relatedSection.className = 'related-cases mt-4';
            relatedSection.innerHTML = `
                <h5>Related Case Studies</h5>
                <ul class="related-cases-list"></ul>
            `;
            contentEl.appendChild(relatedSection);
        }
        
        // Update related cases list
        const relatedList = relatedSection.querySelector('.related-cases-list');
        relatedList.innerHTML = '';
        
        // Show up to 3 related cases
        const casesToShow = relatedCases.slice(0, 3);
        
        casesToShow.forEach(relatedCaseId => {
            const relatedCard = document.querySelector(`.view-case-study-btn[data-case-id="${relatedCaseId}"]`).closest('.case-study-card');
            const title = relatedCard.querySelector('h3').textContent;
            
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <a href="#" class="related-case-link" data-case-id="${relatedCaseId}">${title}</a>
            `;
            relatedList.appendChild(listItem);
        });
        
        // Add click handlers for related case links
        relatedSection.querySelectorAll('.related-case-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const relatedCaseId = this.getAttribute('data-case-id');
                const relatedButton = document.querySelector(`.view-case-study-btn[data-case-id="${relatedCaseId}"]`);
                
                if (relatedButton) {
                    // Hide current case study
                    contentEl.style.display = 'none';
                    
                    // Click the related case study button
                    relatedButton.click();
                }
            });
        });
    }
}

/**
 * Share a case study via social media or email
 * @param {string} caseId - Case study ID
 * @param {string} platform - Sharing platform (twitter, linkedin, email)
 */
function shareCaseStudy(caseId, platform) {
    // Get case study details
    const caseCard = document.querySelector(`.view-case-study-btn[data-case-id="${caseId}"]`).closest('.case-study-card');
    const title = encodeURIComponent(caseCard.querySelector('h3').textContent);
    const summary = encodeURIComponent(caseCard.querySelector('p').textContent);
    
    // Base URL for sharing (this would be the actual URL in a real implementation)
    const shareUrl = encodeURIComponent(`https://aiethicsplatform.example.com/case-studies#case-${caseId}`);
    
    // Share links for different platforms
    const shareLinks = {
        twitter: `https://twitter.com/intent/tweet?text=${title}&url=${shareUrl}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${shareUrl}`,
        email: `mailto:?subject=${title}&body=${summary}%0A%0ARead more: ${shareUrl}`
    };
    
    // Open share dialog
    if (shareLinks[platform]) {
        window.open(shareLinks[platform], '_blank');
    }
}
