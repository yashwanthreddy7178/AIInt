import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Interview, Feedback, InterviewQuestion
import json

feedback_bp = Blueprint('feedback', __name__)

def init_routes(app):
    # Feedback route
    @app.route('/feedback/<int:interview_id>', methods=['GET'])
    @login_required
    def feedback(interview_id):
        interview = Interview.query.get_or_404(interview_id)
        
        # Check if the interview belongs to the current user
        if interview.user_id != current_user.id:
            flash('You do not have permission to access this feedback.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get the feedback
        feedback = Feedback.query.filter_by(interview_id=interview_id).first()
        
        # If feedback doesn't exist, redirect to the interview
        if not feedback:
            if interview.status != 'completed':
                flash('The interview is not yet completed. Please complete the interview first.', 'info')
                return redirect(url_for('interview', interview_id=interview_id))
            else:
                flash('Feedback is not available for this interview.', 'info')
                return redirect(url_for('dashboard'))
        
        # Get the questions and responses
        questions = InterviewQuestion.query.filter_by(interview_id=interview_id).order_by(InterviewQuestion.question_order).all()
        
        return render_template('feedback.html', 
                               interview=interview,
                               feedback=feedback,
                               questions=questions)
    
    # Fetch question details for feedback page (AJAX)
    @app.route('/feedback/<int:interview_id>/question/<int:question_id>', methods=['GET'])
    @login_required
    def question_details(interview_id, question_id):
        interview = Interview.query.get_or_404(interview_id)
        
        # Check if the interview belongs to the current user
        if interview.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        question = InterviewQuestion.query.get_or_404(question_id)
        
        return jsonify({
            'question': question.question_text,
            'response': question.user_response,
            'analysis': question.ai_analysis,
            'score': question.score
        })
    
    # Get feedback for chart (AJAX)
    @app.route('/feedback/<int:interview_id>/chart-data', methods=['GET'])
    @login_required
    def feedback_chart_data(interview_id):
        interview = Interview.query.get_or_404(interview_id)
        
        # Check if the interview belongs to the current user
        if interview.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Get questions and their scores
        questions = InterviewQuestion.query.filter_by(interview_id=interview_id).order_by(InterviewQuestion.question_order).all()
        
        labels = [f"Q{q.question_order}" for q in questions]
        scores = [q.score for q in questions]
        
        return jsonify({
            'labels': labels,
            'scores': scores
        })
    
    # Get historical performance data (AJAX)
    @app.route('/feedback/historical-data', methods=['GET'])
    @login_required
    def historical_feedback_data():
        # Get all completed interviews for the current user
        interviews = Interview.query.filter_by(
            user_id=current_user.id,
            status='completed'
        ).order_by(Interview.completed_at).all()
        
        # Group by interview type
        data = {}
        for interview_type in ['technical', 'behavioral', 'system_design']:
            type_interviews = [i for i in interviews if i.interview_type == interview_type]
            if type_interviews:
                feedback_list = [i.feedback for i in type_interviews if i.feedback]
                scores = [f.overall_score for f in feedback_list if f]
                dates = [i.completed_at.strftime('%Y-%m-%d') for i in type_interviews if i.feedback]
                
                data[interview_type] = {
                    'labels': dates,
                    'scores': scores
                }
        
        return jsonify(data)
