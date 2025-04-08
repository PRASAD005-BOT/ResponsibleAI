/**
 * AI Ethics Platform - Education Resources JavaScript
 * Handles education resources display and interaction
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize resource filters
    initResourceFilters();
    
    // Initialize view resource buttons
    initViewResourceButtons();
});

/**
 * Initialize resource filter buttons
 */
function initResourceFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const resourceCards = document.querySelectorAll('.resource-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get filter value
            const filter = this.getAttribute('data-filter');
            
            // Update active button
            filterButtons.forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            // Filter resources
            resourceCards.forEach(card => {
                if (filter === 'all' || card.getAttribute('data-resource-type') === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

/**
 * Initialize view resource buttons
 */
function initViewResourceButtons() {
    const viewButtons = document.querySelectorAll('.view-resource-btn');
    
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get resource ID
            const resourceId = this.getAttribute('data-resource-id');
            const contentEl = document.getElementById(`resource-content-${resourceId}`);
            
            if (contentEl) {
                // Toggle content visibility
                if (contentEl.style.display === 'none' || !contentEl.style.display) {
                    contentEl.style.display = 'block';
                    this.textContent = 'Hide Content';
                    
                    // Scroll to content
                    setTimeout(() => {
                        contentEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                } else {
                    contentEl.style.display = 'none';
                    this.textContent = 'View Content';
                }
            }
        });
    });
}

/**
 * Set up interactive components when resources are loaded
 */
function setupInteractiveComponents() {
    // This function would handle any interactive components within resources
    // For example, quizzes, interactive diagrams, etc.
    
    // For now, we'll just log that resources are ready
    console.log('Education resources loaded and ready');
    
    // Set up tooltips for technical terms
    const termElements = document.querySelectorAll('.technical-term');
    
    termElements.forEach(element => {
        // Create tooltip for technical terms
        const term = element.getAttribute('data-term');
        const definition = element.getAttribute('data-definition');
        
        if (term && definition) {
            element.classList.add('tooltip');
            
            const tooltipText = document.createElement('span');
            tooltipText.classList.add('tooltip-text');
            tooltipText.textContent = definition;
            
            element.appendChild(tooltipText);
        }
    });
}

/**
 * Handle resource search functionality
 * @param {string} query - Search query
 */
function searchResources(query) {
    // Normalize search query
    query = query.toLowerCase().trim();
    
    // Get all resource cards
    const resourceCards = document.querySelectorAll('.resource-card');
    
    // Filter resources based on search query
    resourceCards.forEach(card => {
        const title = card.querySelector('h4').textContent.toLowerCase();
        const description = card.querySelector('p').textContent.toLowerCase();
        
        if (title.includes(query) || description.includes(query)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/**
 * Generate a PDF of a resource for downloading
 * @param {string} resourceId - Resource ID
 */
function generateResourcePDF(resourceId) {
    // This would use a library like jsPDF to generate a downloadable PDF
    // For now, we'll just show an alert
    alert('This feature will be available soon. Please check back later.');
}

/**
 * Track resource view for analytics
 * @param {string} resourceId - Resource ID
 * @param {string} resourceTitle - Resource title
 */
function trackResourceView(resourceId, resourceTitle) {
    // This would send analytics data to the server
    // For now, we'll just log to console
    console.log(`Resource viewed: ${resourceTitle} (ID: ${resourceId})`);
}
