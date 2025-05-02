from app import app, db
from models import Interview, Feedback
from sqlalchemy import func

def fix_duplicate_feedback():
    with app.app_context():
        # Find interviews with multiple feedback records
        duplicate_feedback = db.session.query(
            Feedback.interview_id,
            func.count(Feedback.id).label('count')
        ).group_by(Feedback.interview_id).having(func.count(Feedback.id) > 1).all()
        
        for interview_id, count in duplicate_feedback:
            print(f"Interview {interview_id} has {count} feedback records")
            
            # Get all feedback records for this interview
            feedbacks = Feedback.query.filter_by(interview_id=interview_id).all()
            
            # Keep the most recent feedback record
            latest_feedback = max(feedbacks, key=lambda x: x.created_at)
            
            # Delete all other feedback records
            for feedback in feedbacks:
                if feedback.id != latest_feedback.id:
                    print(f"Deleting feedback {feedback.id} for interview {interview_id}")
                    db.session.delete(feedback)
        
        # Add unique constraint to prevent this from happening again
        try:
            db.session.execute('ALTER TABLE feedback ADD CONSTRAINT uq_feedback_interview UNIQUE (interview_id)')
            print("Added unique constraint to feedback table")
        except Exception as e:
            print(f"Error adding unique constraint: {e}")
        
        db.session.commit()
        print("Database cleanup completed")

if __name__ == '__main__':
    fix_duplicate_feedback() 