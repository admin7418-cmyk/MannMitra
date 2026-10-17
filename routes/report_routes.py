from flask import Blueprint, render_template, redirect, url_for, session
from models.journal_model import all_for_user
from models.chat_model import recent
from models.habit_model import all_for_user as all_habits
from services.memory_service import build_memory
from services.gita_service import recommend
from services.report_service import build_weekly_report

report_bp = Blueprint('report', __name__)


@report_bp.route('/report')
@report_bp.route('/reports/weekly')
def weekly_report_page():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('auth.login_page'))
    journals = all_for_user(uid)
    chats = recent(uid, 50)
    habits = all_habits(uid)
    memory = build_memory(journals, chats, habits)
    wisdom = recommend(memory['dominant_theme'] + ' ' + memory['dominant_mood'])
    report = build_weekly_report(journals, chats, habits, memory, wisdom)
    return render_template('reports/weekly.html', report=report, memory=memory)
