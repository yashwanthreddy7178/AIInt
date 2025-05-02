// JavaScript for the feedback page

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the performance chart
    initializePerformanceChart();
    
    // Set up event listeners for question details
    const questionLinks = document.querySelectorAll('.question-link');
    questionLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const questionId = this.dataset.questionId;
            const interviewId = document.getElementById('feedback-container').dataset.interviewId;
            loadQuestionDetails(interviewId, questionId);
        });
    });
    
    // Initialize the historical performance chart if available
    const historicalChartContainer = document.getElementById('historical-performance-chart');
    if (historicalChartContainer) {
        initializeHistoricalChart();
    }
});

// Initialize the performance chart for the current interview
function initializePerformanceChart() {
    const ctx = document.getElementById('performance-chart');
    if (!ctx) return;
    
    const interviewId = document.getElementById('feedback-container').dataset.interviewId;
    
    // Get the chart data from the server
    sendAjaxRequest(
        `/feedback/${interviewId}/chart-data`,
        'GET',
        {},
        function(data) {
            // Create the chart
            const performanceChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Question Scores',
                        data: data.scores,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Score'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Questions'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Score: ${context.raw}/100`;
                                }
                            }
                        }
                    }
                }
            });
        },
        function(status, error) {
            console.error('Error loading chart data:', error);
            document.getElementById('chart-container').innerHTML = '<div class="alert alert-danger">Failed to load chart data</div>';
        }
    );
}

// Load and display details for a specific question
function loadQuestionDetails(interviewId, questionId) {
    // Show loading state
    const detailsContainer = document.getElementById('question-details');
    detailsContainer.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading question details...</p>
        </div>
    `;
    
    // Show the modal
    const detailsModal = new bootstrap.Modal(document.getElementById('question-details-modal'));
    detailsModal.show();
    
    // Fetch the question details
    sendAjaxRequest(
        `/feedback/${interviewId}/question/${questionId}`,
        'GET',
        {},
        function(data) {
            // Format the score
            let scoreClass = 'text-danger';
            if (data.score >= 80) {
                scoreClass = 'text-success';
            } else if (data.score >= 60) {
                scoreClass = 'text-info';
            } else if (data.score >= 40) {
                scoreClass = 'text-warning';
            }
            
            // Update the modal content
            detailsContainer.innerHTML = `
                <div class="question-detail">
                    <h5 class="mb-3">Question:</h5>
                    <p class="mb-4">${data.question}</p>
                    
                    <h5 class="mb-3">Your Response:</h5>
                    <div class="card mb-4">
                        <div class="card-body">
                            <p>${data.response || '<em>No response provided</em>'}</p>
                        </div>
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0">AI Analysis:</h5>
                        <span class="badge bg-secondary ${scoreClass}">Score: ${data.score}/100</span>
                    </div>
                    <div class="card">
                        <div class="card-body">
                            <p>${data.analysis ? data.analysis.replace(/\n/g, '<br>') : 'No analysis available'}</p>
                        </div>
                    </div>
                </div>
            `;
        },
        function(status, error) {
            console.error('Error loading question details:', error);
            detailsContainer.innerHTML = '<div class="alert alert-danger">Failed to load question details</div>';
        }
    );
}

// Initialize the historical performance chart
function initializeHistoricalChart() {
    const ctx = document.getElementById('historical-performance-chart');
    if (!ctx) return;
    
    // Get the historical data from the server
    sendAjaxRequest(
        '/feedback/historical-data',
        'GET',
        {},
        function(data) {
            // Check if we have data
            if (Object.keys(data).length === 0) {
                document.getElementById('historical-chart-container').innerHTML = 
                    '<div class="alert alert-info">Not enough historical data available yet.</div>';
                return;
            }
            
            // Prepare datasets
            const datasets = [];
            const colors = {
                'technical': 'rgba(75, 192, 192, 0.6)',
                'behavioral': 'rgba(153, 102, 255, 0.6)',
                'system_design': 'rgba(255, 99, 132, 0.6)'
            };
            
            const borderColors = {
                'technical': 'rgba(75, 192, 192, 1)',
                'behavioral': 'rgba(153, 102, 255, 1)',
                'system_design': 'rgba(255, 99, 132, 1)'
            };
            
            const labels = {
                'technical': 'Technical Interviews',
                'behavioral': 'Behavioral Interviews',
                'system_design': 'System Design Interviews'
            };
            
            // Create a dataset for each interview type
            for (const type in data) {
                datasets.push({
                    label: labels[type],
                    data: data[type].scores,
                    backgroundColor: colors[type],
                    borderColor: borderColors[type],
                    borderWidth: 1
                });
            }
            
            // Create the chart
            const historicalChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data[Object.keys(data)[0]].labels, // Use the dates from the first interview type
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Score'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Interview Date'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.dataset.label}: ${context.raw}/100`;
                                }
                            }
                        }
                    }
                }
            });
        },
        function(status, error) {
            console.error('Error loading historical data:', error);
            document.getElementById('historical-chart-container').innerHTML = 
                '<div class="alert alert-danger">Failed to load historical performance data</div>';
        }
    );
}
