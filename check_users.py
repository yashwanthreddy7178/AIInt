from app import app, db
from models import User

with app.app_context():
    total_users = User.query.count()
    print(f"Total users: {total_users}")
    
    if total_users > 0:
        print("\nUsers:")
        for user in User.query.all():
            print(f"- ID: {user.id}, Username: {user.username}, Email: {user.email}") 