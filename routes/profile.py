from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
def profile():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM profile WHERE id=1")
    p = c.fetchone()
    conn.close()
    return render_template("profile.html", profile=p)


import PyPDF2

@profile_bp.route("/profile/save", methods=["POST"])
def save_profile():
    fields = ["name", "email", "phone", "location", "skills",
              "experience", "education", "linkedin", "github", "portfolio", "summary"]

    data = {f: request.form.get(f, "") for f in fields}
    
    # Handle PDF Upload
    resume_file = request.files.get("resume_pdf")
    if resume_file and resume_file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(resume_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        data["resume_text"] = text
        data["resume_filename"] = resume_file.filename

    conn = get_db()
    c = conn.cursor()

    set_clause = ", ".join(f"{k}=?" for k in data)
    values = list(data.values()) + [1]
    c.execute(f"UPDATE profile SET {set_clause} WHERE id=?", values)
    conn.commit()
    conn.close()

    flash("Profile updated successfully!", "success")
    return redirect(url_for("profile.profile"))
