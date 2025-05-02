import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app import db
from models import User, Subscription

auth_bp = Blueprint('auth', __name__)

# Create form classes
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or login.')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    job_title = StringField('Job Title', validators=[Length(max=128)])
    industry = StringField('Industry', validators=[Length(max=128)])
    experience_level = SelectField('Experience Level', 
                                   choices=[('entry', 'Entry Level'), 
                                            ('mid', 'Mid Level'), 
                                            ('senior', 'Senior Level'), 
                                            ('lead', 'Lead/Manager')])
    submit = SubmitField('Update Profile')

def init_routes(app):
    # Login route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Login unsuccessful. Please check email and password.', 'danger')
        return render_template('login.html', form=form)
    
    # Register route
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
            db.session.add(user)
            db.session.flush()  # Flush to get the user.id without committing
            
            # Create a free subscription for the new user
            subscription = Subscription(user_id=user.id, tier='free')
            db.session.add(subscription)
            
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)
    
    # Logout route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    # Dashboard route
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get user's recent interviews - use Interview model query instead of relationship attribute directly
        from models import Interview
        recent_interviews = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.started_at.desc()).limit(5).all()
        
        # Create interview_types dictionary for the template
        interview_types = {
            'technical': Interview.query.filter_by(user_id=current_user.id, interview_type='technical', status='completed').count(),
            'behavioral': Interview.query.filter_by(user_id=current_user.id, interview_type='behavioral', status='completed').count(),
            'system_design': Interview.query.filter_by(user_id=current_user.id, interview_type='system_design', status='completed').count()
        }
        
        return render_template('dashboard.html', interviews=recent_interviews, interview_types=interview_types)
    
    # Profile route
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        form = ProfileForm()
        if form.validate_on_submit():
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.job_title = form.job_title.data
            current_user.industry = form.industry.data
            current_user.experience_level = form.experience_level.data
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('profile'))
        elif request.method == 'GET':
            form.first_name.data = current_user.first_name
            form.last_name.data = current_user.last_name
            form.job_title.data = current_user.job_title
            form.industry.data = current_user.industry
            form.experience_level.data = current_user.experience_level
        
        # Get subscription info
        subscription = current_user.subscription
        return render_template('profile.html', form=form, subscription=subscription)
    
    # Subscription management route
    @app.route('/subscription')
    @login_required
    def subscription():
        subscription = current_user.subscription
        return render_template('subscription.html', subscription=subscription)
    
    # Interview history route
    @app.route('/history')
    @login_required
    def history():
        from models import Interview
        interviews = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.started_at.desc()).all()
        return render_template('history.html', interviews=interviews)
