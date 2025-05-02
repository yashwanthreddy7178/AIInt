// JavaScript for the interview page functionality

let currentQuestionIndex = 0;
let questions = [];
let interviewTimer = null;
let interviewStartTime = null;
let interviewId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the interview
    interviewId = document.getElementById('interview-container').dataset.interviewId;
    
    // Get all questions
    const questionCards = document.querySelectorAll('.question-card');
    questionCards.forEach((card, index) => {
        questions.push({
            id: card.dataset.questionId,
            element: card,
            responseArea: card.querySelector('.response-area'),
            submitButton: card.querySelector('.submit-answer'),
            feedbackArea: card.querySelector('.feedback-area'),
            nextButton: card.querySelector('.next-question'),
            scoreElement: card.querySelector('.question-score')
        });
    });
    
    // Start with the first question
    if (questions.length > 0) {
        showQuestion(0);
        startTimer();
    }
    
    // Set up event listeners for all submit buttons
    questions.forEach((question, index) => {
        if (question.submitButton) {
            question.submitButton.addEventListener('click', function() {
                submitAnswer(index);
            });
        }
        
        if (question.nextButton) {
            question.nextButton.addEventListener('click', function() {
                if (index < questions.length - 1) {
                    showQuestion(index + 1);
                } else {
                    completeInterview();
                }
            });
        }
    });
    
    // Set up the complete interview button
    const completeButton = document.getElementById('complete-interview');
    if (completeButton) {
        completeButton.addEventListener('click', completeInterview);
    }
});

// Show a specific question and hide others
function showQuestion(index) {
    if (index < 0 || index >= questions.length) return;
    
    questions.forEach((q, i) => {
        if (i === index) {
            q.element.classList.add('current');
            q.element.style.display = 'block';
        } else {
            q.element.classList.remove('current');
            q.element.style.display = 'none';
        }
    });
    
    currentQuestionIndex = index;
    
    // Update progress indicator
    updateProgressIndicator();
}

// Submit the answer for a question
function submitAnswer(questionIndex) {
    const question = questions[questionIndex];
    if (!question) return;
    
    const answer = question.responseArea.value.trim();
    if (!answer) {
        alert('Please provide an answer before submitting.');
        return;
    }
    
    // Disable the submit button and show loading state
    question.submitButton.disabled = true;
    question.submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
    
    // Send the answer to the server
    sendAjaxRequest(
        `/interview/${interviewId}/submit_answer`, 
        'POST', 
        {
            question_id: question.id,
            answer: answer
        },
        function(response) {
            // Success callback
            displayFeedback(questionIndex, response);
            question.submitButton.style.display = 'none';
            
            // Enable the next button
            if (question.nextButton) {
                question.nextButton.style.display = 'block';
                
                // Auto-focus on the next button
                setTimeout(() => {
                    question.nextButton.focus();
                }, 100);
            }
        },
        function(status, error) {
            // Error callback
            console.error('Error submitting answer:', error);
            question.submitButton.disabled = false;
            question.submitButton.textContent = 'Submit Answer';
            alert('There was an error analyzing your answer. Please try again.');
        }
    );
}

// Display feedback for a question
function displayFeedback(questionIndex, response) {
    const question = questions[questionIndex];
    if (!question || !response) return;
    
    // Update the score display
    const scorePercentage = response.score;
    let scoreText = 'Needs Improvement';
    let scoreClass = 'text-danger';
    
    if (scorePercentage >= 80) {
        scoreText = 'Excellent';
        scoreClass = 'text-success';
    } else if (scorePercentage >= 60) {
        scoreText = 'Good';
        scoreClass = 'text-info';
    } else if (scorePercentage >= 40) {
        scoreText = 'Fair';
        scoreClass = 'text-warning';
    }
    
    question.scoreElement.textContent = `${scorePercentage}/100 - ${scoreText}`;
    question.scoreElement.className = `question-score ${scoreClass}`;
    
    // Display the analysis
    question.feedbackArea.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">AI Feedback</h5>
            </div>
            <div class="card-body">
                <p>${response.analysis.replace(/\n/g, '<br>')}</p>
            </div>
        </div>
    `;
    
    // Show the feedback area with animation
    question.feedbackArea.style.display = 'block';
    question.feedbackArea.classList.add('fade-in');
}

// Update the progress indicator
function updateProgressIndicator() {
    const progressBar = document.getElementById('interview-progress');
    if (!progressBar) return;
    
    const progressPercentage = ((currentQuestionIndex + 1) / questions.length) * 100;
    progressBar.style.width = `${progressPercentage}%`;
    progressBar.setAttribute('aria-valuenow', progressPercentage);
    
    // Update the progress text
    const progressText = document.getElementById('progress-text');
    if (progressText) {
        progressText.textContent = `Question ${currentQuestionIndex + 1} of ${questions.length}`;
    }
}

// Start the interview timer
function startTimer() {
    interviewStartTime = new Date();
    const timerElement = document.getElementById('interview-timer');
    
    if (!timerElement) return;
    
    interviewTimer = setInterval(function() {
        const currentTime = new Date();
        const elapsedSeconds = Math.floor((currentTime - interviewStartTime) / 1000);
        
        const minutes = Math.floor(elapsedSeconds / 60);
        const seconds = elapsedSeconds % 60;
        
        timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

// Complete the interview and redirect to feedback
function completeInterview() {
    if (interviewTimer) {
        clearInterval(interviewTimer);
    }
    
    // Check if all questions have been answered
    const unansweredQuestions = questions.filter(q => !q.responseArea.value.trim());
    
    if (unansweredQuestions.length > 0) {
        if (!confirm(`You have ${unansweredQuestions.length} unanswered question(s). Are you sure you want to complete the interview?`)) {
            return;
        }
    }
    
    // Create a form to submit
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/interview/${interviewId}/complete`;
    document.body.appendChild(form);
    form.submit();
}
