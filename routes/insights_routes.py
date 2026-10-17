from flask import Blueprint, render_template, redirect, url_for, session
from models.journal_model import all_for_user
from models.chat_model import recent
from models.habit_model import all_for_user as all_habits
from services.memory_service import build_memory, get_suggestions
from services.gita_service import recommend

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/insights')
def insights_page():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('auth.login_page'))
    journals = all_for_user(uid)
    chats = recent(uid, 50)
    habits = all_habits(uid)
    memory = build_memory(journals, chats, habits)
    suggestions = get_suggestions(memory)
    wisdom = recommend(memory['dominant_theme'] + ' ' + memory['dominant_mood'])
    return render_template('insights/insights.html', memory=memory, suggestions=suggestions, wisdom=wisdom)
