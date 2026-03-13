from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from database import get_db
from datetime import datetime

applications_bp = Blueprint("applications", __name__)

STATUS_ORDER = ["saved", "applied", "interviewing", "offered", "rejected"]
STATUS_COLORS = {
    "saved": "#4A9EFF",
    "applied": "#F59E0B",
    "interviewing": "#8B5CF6",
    "offered": "#10B981",
    "rejected": "#EF4444",
}


@applications_bp.route("/applications")
def applications():
    conn = get_db()
    c = conn.cursor()

    filter_status = request.args.get("status", "all")

    if filter_status == "all":
        c.execute("SELECT * FROM applications ORDER BY date_updated DESC")
    else:
        c.execute("SELECT * FROM applications WHERE status=? ORDER BY date_updated DESC", (filter_status,))

    jobs = c.fetchall()

    # Count by status
    counts = {"all": 0}
    for s in STATUS_ORDER:
        c.execute("SELECT COUNT(*) FROM applications WHERE status=?", (s,))
        counts[s] = c.fetchone()[0]
        counts["all"] += counts[s]

    conn.close()
    return render_template("applications.html",
                           jobs=jobs,
                           filter_status=filter_status,
                           counts=counts,
                           status_colors=STATUS_COLORS,
                           status_order=STATUS_ORDER)


@applications_bp.route("/applications/save", methods=["POST"])
def save_job():
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()

    try:
        c.execute("""
            INSERT OR REPLACE INTO applications
            (job_id, title, company, location, salary, job_type, description, apply_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'saved')
        """, (
            data.get("job_id"),
            data.get("title"),
            data.get("company"),
            data.get("location"),
            data.get("salary"),
            data.get("job_type"),
            data.get("description"),
            data.get("apply_url"),
        ))
        conn.commit()
        return jsonify({"success": True, "message": "Job saved to tracker!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        conn.close()


@applications_bp.route("/applications/<int:app_id>/status", methods=["POST"])
def update_status(app_id):
    new_status = request.form.get("status")
    notes = request.form.get("notes", "")

    conn = get_db()
    c = conn.cursor()

    updates = {
        "status": new_status,
        "notes": notes,
        "date_updated": datetime.now().isoformat(),
    }

    if new_status == "applied":
        updates["date_applied"] = datetime.now().isoformat()

    set_clause = ", ".join(f"{k}=?" for k in updates)
    values = list(updates.values()) + [app_id]

    c.execute(f"UPDATE applications SET {set_clause} WHERE id=?", values)
    conn.commit()
    conn.close()

    flash(f"Status updated to '{new_status}'!", "success")
    return redirect(url_for("applications.applications"))


@applications_bp.route("/applications/<int:app_id>/delete", methods=["POST"])
def delete_application(app_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM applications WHERE id=?", (app_id,))
    conn.commit()
    conn.close()
    flash("Application removed.", "info")
    return redirect(url_for("applications.applications"))


@applications_bp.route("/applications/<int:app_id>/notes", methods=["POST"])
def update_notes(app_id):
    notes = request.form.get("notes", "")
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE applications SET notes=?, date_updated=? WHERE id=?",
              (notes, datetime.now().isoformat(), app_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})
