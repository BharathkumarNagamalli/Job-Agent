from flask import Blueprint, render_template, request, jsonify
from database import get_db
from google import genai
from google.genai import types
import os

ai_bp = Blueprint("ai", __name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set. Get a free key from aistudio.google.com")
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_text(prompt):
    client = get_gemini_client()
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        msg = str(e)
        if "RESOURCE_EXHAUSTED" in msg or "code: 429" in msg:
            raise RuntimeError(
                "Gemini API quota/rate limit reached. Please wait a while, "
                "or create a new API key or enable billing in Google AI Studio."
            )
        raise


def get_profile_text():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM profile WHERE id=1")
    p = c.fetchone()
    conn.close()
    if not p:
        return ""
    return f"""
Name: {p['name']}
Skills: {p['skills']}
Experience: {p['experience']}
Education: {p['education']}
Summary: {p['summary'] or 'Fresh graduate seeking software development roles'}
"""


@ai_bp.route("/ai-assistant")
def ai_assistant():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, company FROM applications ORDER BY date_saved DESC")
    saved_jobs = c.fetchall()
    conn.close()
    return render_template("ai_assistant.html", saved_jobs=saved_jobs)


@ai_bp.route("/ai/cover-letter", methods=["POST"])
def generate_cover_letter():
    data = request.get_json()
    job_title = data.get("job_title", "")
    company = data.get("company", "")
    job_description = data.get("description", "")
    tone = data.get("tone", "professional")

    profile = get_profile_text()

    prompt = f"""You are a professional career advisor. Write a compelling cover letter for this job application.

Candidate Profile:
{profile}

Job Details:
- Role: {job_title}
- Company: {company}
- Description: {job_description[:1000] if job_description else 'Not provided'}

Tone: {tone} (professional / enthusiastic / concise)

Write a cover letter that:
1. Opens with a strong hook
2. Highlights relevant skills and experience
3. Shows genuine interest in the company
4. Ends with a confident call to action
5. Is 3-4 paragraphs, ready to send

Output only the cover letter text, no extra commentary."""

    try:
        return jsonify({"success": True, "content": generate_text(prompt)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@ai_bp.route("/ai/interview-prep", methods=["POST"])
def interview_prep():
    data = request.get_json()
    job_title = data.get("job_title", "")
    company = data.get("company", "")
    prep_type = data.get("prep_type", "questions")  # questions / tips / technical

    profile = get_profile_text()

    if prep_type == "questions":
        prompt = f"""You are an experienced technical interviewer. Generate 10 likely interview questions for this role.

Role: {job_title} at {company}
Candidate Skills: {profile}

Mix of:
- 3 behavioral questions (STAR format hints)
- 4 technical questions relevant to the role
- 2 company/culture fit questions
- 1 situational problem-solving question

Format each as:
**Q1: [Question]**
Tip: [Quick hint on how to answer well]

Be specific to {job_title} and realistic."""

    elif prep_type == "technical":
        prompt = f"""Generate 8 technical coding/system questions for a {job_title} interview.

Candidate Profile: {profile}

Include:
- 3 Python/coding questions with expected complexity
- 2 system design or architecture questions
- 2 SQL/database questions
- 1 debugging scenario

For each, provide:
**Q: [Question]**
Focus: [What skill this tests]
Hint: [Key concepts to cover]"""

    else:  # tips
        prompt = f"""Give 10 actionable interview tips for a {job_title} role at {company}.

Candidate Profile: {profile}

Cover:
- Before the interview (research, preparation)
- During the interview (communication, body language)
- Technical demonstration tips
- Questions to ask the interviewer
- Follow-up after the interview

Be specific and practical."""

    try:
        return jsonify({"success": True, "content": generate_text(prompt)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@ai_bp.route("/ai/resume-tips", methods=["POST"])
def resume_tips():
    data = request.get_json()
    job_title = data.get("job_title", "")

    profile = get_profile_text()

    prompt = f"""You are a professional resume coach. Analyze this candidate's profile and give specific resume improvement tips for a {job_title} role.

Profile:
{profile}

Give:
1. 5 specific bullet point improvements for their experience section
2. 3 skills they should highlight or add
3. 2 resume format/structure tips
4. 1 ATS optimization tip for "{job_title}" roles

Be very specific and actionable. Format with clear sections using markdown bold headers."""

    try:
        return jsonify({"success": True, "content": generate_text(prompt)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@ai_bp.route("/ai/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    history = data.get("history", [])

    profile = get_profile_text()

    system_prompt = f"""You are a smart job search assistant helping a software developer find and apply for jobs.

Candidate Profile:
{profile}

You help with:
- Job search strategies
- Resume and cover letter advice
- Interview preparation
- Salary negotiation tips
- Career guidance for tech roles (Python Developer, Full Stack, Backend, Data Analyst)
- Hyderabad/India job market insights

Be conversational, specific, and encouraging. Keep answers concise but helpful."""

    # Build full context with history
    history_text = ""
    for msg in history[-8:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    full_prompt = f"{system_prompt}\n\n{history_text}User: {message}\nAssistant:"

    try:
        return jsonify({"success": True, "content": generate_text(full_prompt)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
