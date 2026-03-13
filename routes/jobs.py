from flask import Blueprint, render_template, request, jsonify
import requests
import os

jobs_bp = Blueprint("jobs", __name__)

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY", "")
JSEARCH_HOST = "jsearch.p.rapidapi.com"

@jobs_bp.route("/")
def dashboard():
    from database import get_db
    conn = get_db()
    c = conn.cursor()

    # Stats
    stats = {}
    for status in ["saved", "applied", "interviewing", "offered", "rejected"]:
        c.execute("SELECT COUNT(*) FROM applications WHERE status=?", (status,))
        stats[status] = c.fetchone()[0]

    stats["total"] = sum(stats.values())

    # Recent applications
    c.execute("""
        SELECT * FROM applications
        ORDER BY date_updated DESC LIMIT 5
    """)
    recent = c.fetchall()

    conn.close()
    return render_template("dashboard.html", stats=stats, recent=recent)


@jobs_bp.route("/search")
def search():
    query = request.args.get("q", "")
    location = request.args.get("location", "India")
    job_type = request.args.get("job_type", "")
    remote = request.args.get("remote", "")
    page = request.args.get("page", "1")

    jobs = []
    error = None

    if query:
        try:
            jobs = search_jobs(query, location, job_type, remote, page)
        except Exception as e:
            error = str(e)

    return render_template("search.html",
                           jobs=jobs,
                           query=query,
                           location=location,
                           job_type=job_type,
                           remote=remote,
                           page=int(page),
                           error=error)


@jobs_bp.route("/job/<job_id>")
def job_detail(job_id):
    """Fetch and show a single job's details."""
    from database import get_db

    # Check if already saved
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM applications WHERE job_id=?", (job_id,))
    saved = c.fetchone()
    conn.close()

    # Fetch from API
    job = None
    error = None
    try:
        job = get_job_details(job_id)
    except Exception as e:
        error = str(e)

    return render_template("job_detail.html", job=job, saved=saved, error=error)


@jobs_bp.route("/api/search")
def api_search():
    """AJAX job search endpoint."""
    query = request.args.get("q", "")
    location = request.args.get("location", "India")
    job_type = request.args.get("job_type", "")
    remote = request.args.get("remote", "")
    page = request.args.get("page", "1")

    try:
        jobs = search_jobs(query, location, job_type, remote, page)
        return jsonify({"success": True, "jobs": jobs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def search_jobs(query, location="India", job_type="", remote="", page="1"):
    """Call JSearch RapidAPI to find jobs."""
    if not JSEARCH_API_KEY:
        raise ValueError("JSEARCH_API_KEY not set. Get a free key from rapidapi.com/jsearch")

    search_query = f"{query} in {location}"
    if remote == "1":
        search_query += " remote"

    params = {
        "query": search_query,
        "page": page,
        "num_pages": "1",
        "date_posted": "all",
    }
    if job_type:
        params["employment_types"] = job_type.upper()

    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": JSEARCH_HOST,
    }

    try:
        resp = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers=headers,
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
    except requests.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status == 429:
            raise RuntimeError(
                "Job search API rate limit reached. Please wait a minute and try again."
            )
        if status == 403:
            raise RuntimeError(
                "Access to the JSearch API was forbidden. "
                "Please check that your RapidAPI subscription for JSearch is active "
                "and that the JSEARCH_API_KEY in your .env matches the key shown there."
            )
        raise

    data = resp.json()

    jobs = []
    for j in data.get("data", []):
        jobs.append({
            "id": j.get("job_id"),
            "title": j.get("job_title", "N/A"),
            "company": j.get("employer_name", "N/A"),
            "location": format_location(j),
            "salary": format_salary(j),
            "job_type": j.get("job_employment_type", ""),
            "remote": j.get("job_is_remote", False),
            "description": j.get("job_description", "")[:500],
            "apply_url": j.get("job_apply_link", ""),
            "posted": j.get("job_posted_at_datetime_utc", ""),
            "logo": j.get("employer_logo", ""),
        })
    return jobs


def get_job_details(job_id):
    """Get full job details by ID."""
    if not JSEARCH_API_KEY:
        raise ValueError("JSEARCH_API_KEY not set.")

    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": JSEARCH_HOST,
    }
    resp = requests.get(
        "https://jsearch.p.rapidapi.com/job-details",
        headers=headers,
        params={"job_id": job_id, "extended_publisher_details": "false"},
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    j = data.get("data", [{}])[0]

    return {
        "id": j.get("job_id"),
        "title": j.get("job_title", "N/A"),
        "company": j.get("employer_name", "N/A"),
        "location": format_location(j),
        "salary": format_salary(j),
        "job_type": j.get("job_employment_type", ""),
        "remote": j.get("job_is_remote", False),
        "description": j.get("job_description", ""),
        "apply_url": j.get("job_apply_link", ""),
        "posted": j.get("job_posted_at_datetime_utc", ""),
        "logo": j.get("employer_logo", ""),
        "qualifications": j.get("job_required_skills", []),
        "highlights": j.get("job_highlights", {}),
    }


def format_location(j):
    parts = []
    if j.get("job_city"):
        parts.append(j["job_city"])
    if j.get("job_state"):
        parts.append(j["job_state"])
    if j.get("job_country"):
        parts.append(j["job_country"])
    return ", ".join(parts) if parts else "Not specified"


def format_salary(j):
    mn = j.get("job_min_salary")
    mx = j.get("job_max_salary")
    period = j.get("job_salary_period", "")
    if mn and mx:
        return f"${mn:,.0f} - ${mx:,.0f} / {period}"
    elif mn:
        return f"${mn:,.0f}+ / {period}"
    return "Not disclosed"
