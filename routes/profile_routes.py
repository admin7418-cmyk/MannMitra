import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import find_by_id, update_profile
from models.journal_model import all_for_user
from models.chat_model import recent
from models.habit_model import all_for_user as all_habits, get_badges
from datetime import datetime, timedelta

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile_page():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('auth.login_page'))

    user = find_by_id(uid)
    if not user:
        user = {'id': uid, 'name': 'Student', 'email': 'student@college.edu', 'role': 'user', 'preferences': {}}
    journals = all_for_user(uid)
    chats = recent(uid, 100)
    habits = all_habits(uid)

    # Compute streak
    dates = {r['created_at'][:10] for r in journals}
    day = datetime.now().date()
    streak = 0
    while day.isoformat() in dates:
        streak += 1
        day -= timedelta(days=1)

    completed_habits = sum(int(h.get('completed', 0)) for h in habits)
    badges = get_badges(len(journals), completed_habits, streak)

    # Decode preferences
    prefs = {}
    if user:
        raw = user.get('preferences')
        if isinstance(raw, dict):
            prefs = raw
        elif isinstance(raw, str):
            try:
                prefs = json.loads(raw)
            except Exception:
                prefs = {}

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        language = request.form.get('language', 'en').strip()
        if name:
            update_profile(uid, name=name, language=language)
            session['lang'] = language
            flash('Profile and preferences updated successfully! ✨', 'success')
            return redirect(url_for('profile.profile_page'))

    return render_template('profile/profile.html',
                           user=user,
                           prefs=prefs,
                           journals_count=len(journals),
                           chats_count=len(chats),
                           habits_count=len(habits),
                           completed_habits=completed_habits,
                           streak=streak,
                           badges=badges)
