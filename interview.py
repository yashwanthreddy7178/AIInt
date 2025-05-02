import os
import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from models import User, Interview, InterviewQuestion, Feedback
from ai_integration import generate_interview_questions, analyze_response

interview_bp = Blueprint('interview', __name__)

class InterviewSetupForm(FlaskForm):
    interview_type = SelectField('Interview Type', 
                               choices=[('coding', 'Coding Interview'), 
                                       ('ml_design', 'ML System Design Interview'),
                                       ('system_design', 'System Design Interview'),
                                       ('sql', 'SQL Interview'),
                                       ('ml_theory', 'ML Theory Interview'),
                                       ('math', 'Math/Stats/Logic Interview'),
                                       ('custom', 'Custom Interview')],
                               validators=[DataRequired()])
    position = StringField('Position/Role', validators=[DataRequired(), Length(max=128)])
    submit = SubmitField('Start Interview')

def init_routes(app):
    # Interview setup route
    @app.route('/interview/setup', methods=['GET', 'POST'])
    @login_required
    def interview_setup():
        form = InterviewSetupForm()
        if form.validate_on_submit():
            # Create a new interview
            interview = Interview(
                user_id=current_user.id,
                interview_type=form.interview_type.data,
                interview_position=form.position.data,
                started_at=datetime.utcnow(),
                status='in_progress'
            )
            db.session.add(interview)
            db.session.flush()  # Flush to get the interview.id without committing
            
            # Generate interview questions based on the selected type and position
            questions = generate_interview_questions(
                interview_type=form.interview_type.data,
                position=form.position.data
            )
            
            # Add questions to the database
            for i, question in enumerate(questions):
                interview_question = InterviewQuestion(
                    interview_id=interview.id,
                    question_text=question['question'],
                    question_order=i + 1,
                    question_type=question.get('question_type', form.interview_type.data)
                )
                
                # Store schema for SQL questions
                if form.interview_type.data == 'sql' and 'schema' in question:
                    interview_question.schema = question['schema']
                
                db.session.add(interview_question)
            
            db.session.commit()
            return redirect(url_for('interview', interview_id=interview.id))
        
        return render_template('interview/setup.html', form=form)
    
    # Active interview route
    @app.route('/interview/<int:interview_id>', methods=['GET'])
    @login_required
    def interview(interview_id):
        interview = Interview.query.get_or_404(interview_id)
        
        # Check if the interview belongs to the current user
        if interview.user_id != current_user.id:
            flash('You do not have permission to access this interview.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Check if the interview is already completed
        if interview.status == 'completed':
            return redirect(url_for('feedback', interview_id=interview_id))
        
        # Get the interview questions
        questions = InterviewQuestion.query.filter_by(interview_id=interview_id).order_by(InterviewQuestion.question_order).all()
        
        # Select template based on interview type
        template_map = {
            'coding': 'interview/coding_interview.html',
            'ml_design': 'interview/ml_design_interview.html',
            'system_design': 'interview/system_design_interview.html',
            'sql': 'interview/sql_interview.html',
            'ml_theory': 'interview/ml_theory_interview.html',
            'math': 'interview/math_interview.html',
            'custom': 'interview.html'
        }
        
        template = template_map.get(interview.interview_type, 'interview.html')
        return render_template(template, interview=interview, questions=questions)
    
    # Submit answer route (AJAX)
    @app.route('/interview/<int:interview_id>/submit_answer', methods=['POST'])
    @login_required
    def submit_answer(interview_id):
        interview = Interview.query.get_or_404(interview_id)
        
        # Check if the interview belongs to the current user
        if interview.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        data = request.json
        question_id = data.get('question_id')
        answer = data.get('answer', '')
        language = data.get('language', '')
        
        question = InterviewQuestion.query.get_or_404(question_id)
        
        # Save the user's response
        question.user_response = answer
        question.language = language
        
        # Analyze the response
        analysis_result = analyze_response(
            question_text=question.question_text,
            question_type=question.question_type,
            interview_type=interview.interview_type,
            answer=answer,
            language=language
        )
        
        # Save the analysis and score
        question.ai_analysis = analysis_result['analysis']
        question.score = analysis_result['score']
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'score': analysis_result['score'],
            'analysis': analysis_result['analysis']
        })
    
    # Complete interview route
    @app.route('/interview/<int:interview_id>/complete', methods=['POST'])
    @login_required
    def complete_interview(interview_id):
        interview = Interview.query.get_or_404(interview_id)
        
        # Check if the interview belongs to the current user
        if interview.user_id != current_user.id:
            flash('You do not have permission to complete this interview.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Update the interview status
        interview.status = 'completed'
        interview.completed_at = datetime.utcnow()
        
        # Calculate the duration
        if interview.started_at:
            duration = (interview.completed_at - interview.started_at).total_seconds()
            interview.duration = int(duration)
        
        # Generate overall feedback
        questions = interview.questions
        
        # Calculate the overall score (average of question scores)
        scores = [q.score for q in questions if q.score is not None]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        # Get all question responses to build comprehensive feedback
        question_responses = []
        for q in questions:
            question_responses.append({
                'question': q.question_text,
                'response': q.user_response,
                'analysis': q.ai_analysis,
                'score': q.score
            })
        
        # Create feedback entry using AI analysis
        from ai_integration import generate_interview_feedback
        feedback_data = generate_interview_feedback(
            interview_type=interview.interview_type,
            position=interview.interview_position,
            question_responses=question_responses,
            overall_score=overall_score
        )
        
        feedback = Feedback(
            interview_id=interview.id,
            overall_score=overall_score,
            strengths=feedback_data['strengths'],
            weaknesses=feedback_data['weaknesses'],
            improvement_suggestions=feedback_data['improvement_suggestions'],
            detailed_feedback=feedback_data['detailed_feedback']
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return redirect(url_for('feedback', interview_id=interview.id))
