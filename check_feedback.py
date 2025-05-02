from app import app, db
from models import Interview, Feedback
import traceback

def check_feedback_scores():
    try:
        with app.app_context():
            print("Starting feedback check...")
            
            # Check total interviews
            total_interviews = Interview.query.count()
            print(f"\nTotal interviews in database: {total_interviews}")
            
            # Get all completed interviews with feedback
            interviews = Interview.query.filter_by(status='completed').all()
            print(f"Number of completed interviews: {len(interviews)}")
            
            print("\nDetailed Feedback Check:")
            print("-" * 50)
            
            if not interviews:
                print("No completed interviews found in the database")
                return
            
            for interview in interviews:
                print(f"\nInterview ID: {interview.id}")
                print(f"Type: {interview.interview_type}")
                print(f"Status: {interview.status}")
                
                if interview.feedback:
                    print(f"Feedback ID: {interview.feedback.id}")
                    print(f"Overall Score: {interview.feedback.overall_score}")
                    print(f"Created At: {interview.feedback.created_at}")
                else:
                    print("No feedback found")
                
                print("-" * 50)
            
            # Check the average score calculation
            completed_interviews = [i for i in interviews if i.status == 'completed']
            interviews_with_feedback = [i for i in completed_interviews if i.feedback]
            
            if interviews_with_feedback:
                total_score = sum(i.feedback.overall_score for i in interviews_with_feedback)
                avg_score = total_score / len(interviews_with_feedback)
                print(f"\nCalculated Average Score: {avg_score:.1f}/100")
            else:
                print("\nNo interviews with feedback found for average calculation")
                
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())

if __name__ == '__main__':
    check_feedback_scores() 