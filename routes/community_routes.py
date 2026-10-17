from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from models.community_model import create, recent, like_post, report_post

community_bp = Blueprint("community", __name__)

@community_bp.route("/community", methods=["GET", "POST"])
def community_page():
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login_page"))

    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if message:
            create(uid, message, datetime.now().isoformat())
            flash("Your encouraging thought was shared anonymously ✨", "success")
            return redirect(url_for("community.community_page"))

    sort_by = request.args.get("sort", "recent")
    posts = recent(limit=50, sort_by=sort_by)
    return render_template("community/community.html", posts=posts, sort_by=sort_by)

@community_bp.post("/community/like/<post_id>")
def like_action(post_id):
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login_page"))
    like_post(post_id)
    return redirect(url_for("community.community_page"))

@community_bp.post("/community/report/<post_id>")
def report_action(post_id):
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login_page"))
    report_post(post_id)
    flash("Post flagged for administrator review. Thank you for keeping our community mindful.", "success")
    return redirect(url_for("community.community_page"))

