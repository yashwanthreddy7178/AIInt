// Main JavaScript file for common functionality across the site

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add animation to alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.classList.add('fade-in');
        
        // Set up auto-dismiss for alerts with the auto-dismiss class
        if (alert.classList.contains('auto-dismiss')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
    
    // Handle subscription toggle (placeholder functionality)
    const subscriptionToggle = document.getElementById('subscription-toggle');
    if (subscriptionToggle) {
        subscriptionToggle.addEventListener('change', function() {
            alert('This would change your subscription in a real application.');
        });
    }
    
    // Initialize any charts on the page if Chart.js is loaded
    initializeCharts();
});

// Function to initialize charts if Chart.js is available
function initializeCharts() {
    if (typeof Chart !== 'undefined') {
        // If there are charts to be initialized, they'll call their own initialization functions
        console.log('Chart.js is available for chart initialization');
    }
}

// Utility function to format dates
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Utility function to format time duration
function formatDuration(seconds) {
    if (!seconds) return 'N/A';
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    return `${minutes}m ${remainingSeconds}s`;
}

// Function to handle Ajax requests
function sendAjaxRequest(url, method, data, successCallback, errorCallback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            const response = JSON.parse(xhr.responseText);
            if (successCallback) successCallback(response);
        } else {
            console.error('Request failed with status:', xhr.status);
            if (errorCallback) errorCallback(xhr.status, xhr.responseText);
        }
    };
    
    xhr.onerror = function() {
        console.error('Request failed');
        if (errorCallback) errorCallback(0, 'Network error');
    };
    
    xhr.send(JSON.stringify(data));
}
