from flask import Blueprint,render_template,request,redirect,url_for,session,flash
from datetime import datetime
from models.journal_model import create,all_for_user,delete,find,update
from services.sentiment_service import analyze
journal_bp=Blueprint("journal",__name__)
def uid(): return session.get("user_id")
@journal_bp.route("/journal",methods=["GET","POST"])
def journal_page():
    user=uid()
    if not user:return redirect(url_for("auth.login_page"))
    if request.method=="POST":
        title=request.form.get("title","").strip() or "My Journal"; body=request.form.get("body","").strip()
        if not body: flash("Please write something first.","error"); return redirect(url_for("journal.journal_page"))
        score,mood=analyze(body); create(user,title,body,mood,score,datetime.now().isoformat()); flash("Journal saved ✨","success"); return redirect(url_for("journal.journal_page"))
    return render_template("journal/journal.html",journals=all_for_user(user))
@journal_bp.route("/journal/edit/<journal_id>",methods=["GET","POST"])
def edit_page(journal_id):
    user=uid()
    if not user:return redirect(url_for("auth.login_page"))
    journal=find(journal_id,user)
    if not journal: flash("Journal entry not found.","error"); return redirect(url_for("journal.journal_page"))
    if request.method=="POST":
        title=request.form.get("title","").strip() or "My Journal"; body=request.form.get("body","").strip()
        if not body: flash("Please write something first.","error"); return render_template("journal/edit.html",journal=journal)
        score,mood=analyze(body); update(journal_id,user,title,body,mood,score,datetime.now().isoformat()); flash("Journal updated successfully.","success"); return redirect(url_for("journal.journal_page"))
    return render_template("journal/edit.html",journal=journal)
@journal_bp.route("/journal/delete/<journal_id>",methods=["POST"])
def delete_page(journal_id):
    user=uid()
    if not user:return redirect(url_for("auth.login_page"))
    delete(journal_id,user); flash("Journal entry deleted.","success"); return redirect(url_for("journal.journal_page"))
