from flask import Flask
from database import init_db
from routes.jobs import jobs_bp
from routes.applications import applications_bp
from routes.ai_assistant import ai_bp
from routes.profile import profile_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "job-agent-secret-2024")

# Register blueprints
app.register_blueprint(jobs_bp)
app.register_blueprint(applications_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(profile_bp)

# Initialize DB
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
