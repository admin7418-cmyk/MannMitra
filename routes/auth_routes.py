from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from services.auth_service import register, authenticate
from models.user_model import find_by_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET","POST"])
def register_page():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")

        if not name or not email or len(password) < 6:
            flash("Please enter a valid name, email, and password of at least 6 characters.", "error")
            return render_template("auth/register.html")

        if find_by_email(email):
            flash("An account with this email is already registered. Please sign in.", "error")
            return redirect(url_for("auth.login_page"))

        try:
            uid = register(name, email, password, datetime.now().isoformat())
            flash("Account created successfully! Please sign in to begin.", "success")
            return redirect(url_for("auth.login_page"))
        except Exception as e:
            flash("Registration could not be completed. Please try again with valid details.", "error")
            return render_template("auth/register.html")

    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET","POST"])
def login_page():
    if request.method == "POST":
        identifier = (request.form.get("email") or request.form.get("username") or "").strip()
        password = request.form.get("password","")

        user = authenticate(identifier, password)
        if user:
            session.permanent = True
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["role"] = user.get("role", "user")
            if user.get("role") == "admin":
                session["admin_logged_in"] = True
            flash(f"Welcome back, {user['name']}! 🌿", "success")
            return redirect(url_for("dashboard.dashboard_page"))

        flash("Invalid email/username or password. Please verify and try again.", "error")

    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out safely. Come back anytime.", "success")
    return redirect(url_for("home_routes.home"))

