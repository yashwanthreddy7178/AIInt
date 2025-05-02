from app import app, db
from models import Interview, Feedback

with app.app_context():
    total_interviews = Interview.query.count()
    completed_interviews = Interview.query.filter_by(status='completed').count()
    interviews_with_feedback = Interview.query.filter_by(status='completed').join(Feedback).count()
    
    print(f"Total interviews: {total_interviews}")
    print(f"Completed interviews: {completed_interviews}")
    print(f"Interviews with feedback: {interviews_with_feedback}")
    
    if completed_interviews > 0:
        print("\nCompleted interviews:")
        for interview in Interview.query.filter_by(status='completed').all():
            print(f"- ID: {interview.id}, Type: {interview.interview_type}, Feedback: {'Yes' if interview.feedback else 'No'}") 