from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import date
from models.habit_model import add, all_for_user, toggle, delete, get_badges
from models.journal_model import all_for_user as all_journals

habit_bp = Blueprint("habits", __name__)

@habit_bp.route("/habits", methods=["GET", "POST"])
def habit_page():
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login_page"))

    if request.method == "POST":
        action = request.form.get("action")
        toggle_id = request.form.get("toggle_id")
        delete_id = request.form.get("delete_id")

        if toggle_id:
            toggle(toggle_id, uid)
            return redirect(url_for("habits.habit_page"))
        elif delete_id:
            delete(delete_id, uid)
            flash("Habit removed.", "info")
            return redirect(url_for("habits.habit_page"))
        else:
            name = request.form.get("name", "").strip()
            if name:
                add(uid, name, date.today().isoformat())
                flash("New wellness habit added! Consistency over perfection ✨", "success")
                return redirect(url_for("habits.habit_page"))

    habits = all_for_user(uid)
    journals = all_journals(uid)
    completed_count = sum(int(h.get('completed', 0)) for h in habits)
    max_streak = max([int(h.get('streak', 0)) for h in habits], default=0)
    badges = get_badges(len(journals), completed_count, max_streak)

    return render_template("habits/habits.html",
                           habits=habits,
                           completed_count=completed_count,
                           max_streak=max_streak,
                           badges=badges)

@habit_bp.post("/habits/delete/<habit_id>")
def delete_habit_action(habit_id):
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login_page"))
    delete(habit_id, uid)
    flash("Habit deleted.", "info")
    return redirect(url_for("habits.habit_page"))

