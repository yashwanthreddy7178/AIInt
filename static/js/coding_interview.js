document.addEventListener('DOMContentLoaded', function() {
    // Get interview ID from container
    const interviewId = document.getElementById('interview-container').dataset.interviewId;

    // Initialize CodeMirror editors
    const editors = {};
    const languageModes = {
        'python': 'python',
        'javascript': 'javascript',
        'java': 'text/x-java',
        'cpp': 'text/x-c++src'
    };

    // Initialize all code editors
    document.querySelectorAll('.code-editor').forEach(textarea => {
        const editor = CodeMirror.fromTextArea(textarea, {
            mode: 'python',
            theme: 'monokai',
            lineNumbers: true,
            indentUnit: 4,
            smartIndent: true,
            lineWrapping: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            extraKeys: {
                "Tab": "indentMore",
                "Shift-Tab": "indentLess"
            }
        });
        editors[textarea.id] = editor;
    });

    // Handle language selection changes
    document.querySelectorAll('.language-select').forEach(select => {
        select.addEventListener('change', function() {
            const editorId = this.id.replace('language-', 'code-');
            const editor = editors[editorId];
            const mode = languageModes[this.value];
            editor.setOption('mode', mode);
        });
    });

    // Handle answer submission
    document.querySelectorAll('.submit-answer').forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.question-card');
            const questionId = card.dataset.questionId;
            const editor = editors[`code-${questionId}`];
            const language = document.querySelector(`#language-${questionId}`).value;
            const code = editor.getValue();

            // Show loading state
            this.disabled = true;
            this.textContent = 'Submitting...';

            // Submit the answer
            fetch(`/interview/${interviewId}/submit_answer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_id: questionId,
                    answer: code,
                    language: language
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show feedback
                    const feedbackArea = card.querySelector('.feedback-area');
                    const scoreElement = feedbackArea.querySelector('.question-score');
                    const feedbackContent = feedbackArea.querySelector('.feedback-content');
                    
                    if (feedbackArea && scoreElement && feedbackContent) {
                        feedbackArea.style.display = 'block';
                        scoreElement.textContent = `${data.score}/100`;
                        feedbackContent.innerHTML = data.analysis;
                        
                        // Hide submit button and show next button
                        this.style.display = 'none';
                        card.querySelector('.next-question').style.display = 'block';
                        
                        // Update progress
                        updateProgress();
                    } else {
                        console.error('Missing feedback elements');
                        alert('Error displaying feedback. Please try again.');
                    }
                } else {
                    alert('Error submitting answer: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error submitting answer. Please try again.');
            })
            .finally(() => {
                this.disabled = false;
                this.textContent = 'Submit Solution';
            });
        });
    });

    // Handle next question button
    document.querySelectorAll('.next-question').forEach(button => {
        button.addEventListener('click', function() {
            const currentCard = this.closest('.question-card');
            const nextCard = currentCard.nextElementSibling;
            
            if (nextCard && nextCard.classList.contains('question-card')) {
                currentCard.classList.remove('current');
                nextCard.classList.add('current');
                nextCard.scrollIntoView({ behavior: 'smooth' });
            } else {
                // Show completion card
                document.getElementById('interview-complete-card').style.display = 'block';
                currentCard.classList.remove('current');
            }
        });
    });

    // Initialize timer
    let startTime = new Date().getTime();
    const timerElement = document.getElementById('interview-timer');
    
    setInterval(() => {
        const currentTime = new Date().getTime();
        const elapsedTime = Math.floor((currentTime - startTime) / 1000);
        const minutes = Math.floor(elapsedTime / 60);
        const seconds = elapsedTime % 60;
        timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);

    // Show first question
    document.querySelector('.question-card').classList.add('current');

    // Function to update progress
    function updateProgress() {
        const totalQuestions = document.querySelectorAll('.question-card').length;
        const answeredQuestions = document.querySelectorAll('.question-card .feedback-area[style*="display: block"]').length;
        const progress = (answeredQuestions / totalQuestions) * 100;
        
        document.getElementById('interview-progress').style.width = `${progress}%`;
        document.getElementById('progress-text').textContent = `Question ${answeredQuestions + 1} of ${totalQuestions}`;
    }
}); 