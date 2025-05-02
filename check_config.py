import os
from app import app

with app.app_context():
    print("Environment variables:")
    print(f"DATABASE_URL = {os.environ.get('DATABASE_URL')}")
    print("\nFlask config:")
    print(f"SQLALCHEMY_DATABASE_URI = {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Instance path = {app.instance_path}")
    print("\nDatabase files in instance directory:")
    instance_files = os.listdir(app.instance_path)
    for file in instance_files:
        if file.endswith('.db'):
            file_path = os.path.join(app.instance_path, file)
            size = os.path.getsize(file_path)
            print(f"- {file} ({size} bytes)") 