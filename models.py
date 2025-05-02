from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User profile information
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    job_title = db.Column(db.String(128))
    industry = db.Column(db.String(128))
    experience_level = db.Column(db.String(64))
    
    # Relationships
    interviews = db.relationship('Interview', backref='user', lazy=True, cascade="all, delete-orphan")
    subscription = db.relationship('Subscription', backref='user', lazy=True, uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<User {self.username}>'

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tier = db.Column(db.String(20), default='free', nullable=False)  # 'free', 'premium'
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Subscription {self.tier} for User {self.user_id}>'

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    interview_type = db.Column(db.String(50), nullable=False)  # 'technical', 'behavioral', 'system_design'
    interview_position = db.Column(db.String(128))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # Duration in seconds
    status = db.Column(db.String(20), default='in_progress')  # 'in_progress', 'completed', 'abandoned'
    
    # Relationships
    questions = db.relationship('InterviewQuestion', backref='interview', lazy=True, cascade="all, delete-orphan")
    feedback = db.relationship('Feedback', backref='interview', lazy=True, uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Interview {self.id} ({self.interview_type}) for User {self.user_id}>'

class InterviewQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_order = db.Column(db.Integer, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    user_response = db.Column(db.Text)
    ai_analysis = db.Column(db.Text)
    score = db.Column(db.Integer)
    language = db.Column(db.String(50))  # For coding questions
    schema = db.Column(db.JSON)  # For SQL questions to store database schema
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Question {self.id} for Interview {self.interview_id}>'

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    overall_score = db.Column(db.Float)  # Overall score from 0-100
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)
    improvement_suggestions = db.Column(db.Text)
    detailed_feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feedback {self.id} for Interview {self.interview_id}>'
