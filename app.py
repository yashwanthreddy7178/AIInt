import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, render_template
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_migrate import Migrate

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# Import models and create tables
with app.app_context():
    # Import models
    from models import User, Interview, InterviewQuestion, Feedback, Subscription  # noqa: F401
    
    # Create all tables
    db.create_all()

# Import routes
from auth import auth_bp
from interview import interview_bp
from feedback import feedback_bp

# Add custom template filters
import re

@app.template_filter('nl2br')
def nl2br(value):
    """Convert newlines to <br> tags."""
    if value is None:
        return ""
    result = re.sub(r'\r\n|\r|\n', '<br>\n', str(value))
    return Markup(result)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(interview_bp)
app.register_blueprint(feedback_bp)

# Import and register user loader
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and register routes from auth.py
from auth import init_routes as init_auth_routes
init_auth_routes(app)

# Import and register routes from interview.py
from interview import init_routes as init_interview_routes
init_interview_routes(app)

# Import and register routes from feedback.py
from feedback import init_routes as init_feedback_routes
init_feedback_routes(app)

# Home route
@app.route('/')
def index():
    return render_template('index.html')
