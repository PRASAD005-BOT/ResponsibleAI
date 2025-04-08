/**
 * AI Ethics Platform - Main JavaScript File
 * Handles common functionality across the platform
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize tabs
    initTabs();
    
    // Handle messages fade-out
    initAlertDismiss();
    
    // Initialize mobile navigation menu
    initMobileNav();
    
    console.log('AI Ethics Platform initialized successfully.');
});

/**
 * Initialize tooltip functionality
 */
function initTooltips() {
    const tooltips = document.querySelectorAll('.tooltip');
    
    tooltips.forEach(tooltip => {
        const tooltipText = tooltip.querySelector('.tooltip-text');
        if (!tooltipText) return;
        
        tooltip.addEventListener('mouseenter', () => {
            tooltipText.style.visibility = 'visible';
            tooltipText.style.opacity = '1';
        });
        
        tooltip.addEventListener('mouseleave', () => {
            tooltipText.style.visibility = 'hidden';
            tooltipText.style.opacity = '0';
        });
    });
}

/**
 * Initialize tab functionality
 */
function initTabs() {
    const tabLinks = document.querySelectorAll('.tab-link');
    
    tabLinks.forEach(tabLink => {
        tabLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            const tabContainer = this.closest('.tab-container');
            if (!tabContainer) return;
            
            // Remove active class from all tabs
            tabContainer.querySelectorAll('.tab-link').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Hide all tab panes
            tabContainer.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            
            // Show the selected tab pane
            const target = this.getAttribute('href');
            const targetPane = document.querySelector(target);
            if (targetPane) {
                targetPane.classList.add('active');
            }
        });
    });
}

/**
 * Initialize alert message dismissal
 */
function initAlertDismiss() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
        
        // Add click to dismiss
        alert.addEventListener('click', () => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        });
    });
}

/**
 * Initialize mobile navigation
 */
function initMobileNav() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.navbar-nav');
    
    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
        });
    }
}

/**
 * Format number for display
 * @param {number} num - Number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number
 */
function formatNumber(num, decimals = 2) {
    return num.toFixed(decimals);
}

/**
 * Format percentage for display
 * @param {number} value - Value to format (0-1)
 * @returns {string} Formatted percentage
 */
function formatPercent(value) {
    return (value * 100).toFixed(1) + '%';
}

/**
 * Helper function to show loading state
 * @param {string} elementId - ID of element to show loading state
 * @param {string} message - Optional loading message
 */
function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.innerHTML = `
        <div class="loading-container text-center">
            <div class="spinner"></div>
            <p class="mt-2">${message}</p>
        </div>
    `;
}

/**
 * Helper function to show error message
 * @param {string} elementId - ID of element to show error
 * @param {string} message - Error message
 */
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.innerHTML = `
        <div class="alert alert-error">
            <p><strong>Error:</strong> ${message}</p>
            <p>Please try again or contact support if the problem persists.</p>
        </div>
    `;
}

/**
 * Ajax function for making API requests
 * @param {string} url - URL to make request to
 * @param {Object} options - Request options
 * @returns {Promise} - Promise that resolves with response data
 */
function ajaxRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    // Add CSRF token for POST requests
    if (finalOptions.method === 'POST') {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        finalOptions.headers['X-CSRFToken'] = csrfToken;
    }
    
    return fetch(url, finalOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.status}`);
            }
            return response.json();
        });
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {boolean} - Whether copy was successful
 */
function copyToClipboard(text) {
    // Create temporary element
    const el = document.createElement('textarea');
    el.value = text;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    
    // Select and copy text
    el.select();
    const success = document.execCommand('copy');
    
    // Clean up
    document.body.removeChild(el);
    return success;
}
