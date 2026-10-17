from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime
from models.chat_model import save, recent
from models.journal_model import all_for_user
from services.ai_service import generate_ai_reply, build_profile

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['GET', 'POST'])
def chat_page():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('auth.login_page'))

    journals = all_for_user(uid)
    lang = request.values.get('lang', session.get('lang', 'en')).lower().strip()
    if lang not in ['en', 'hi', 'hinglish']:
        lang = 'en'
    session['lang'] = lang

    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message:
            history = recent(uid, 10)
            result = generate_ai_reply(message, journals, history, lang=lang, user_id=uid)
            gita = result.get('gita') or {}
            save(uid, message, result['reply'], datetime.now().isoformat(),
                 result.get('intent', 'friendly'), gita.get('reference', ''), language=lang)

    history = recent(uid, 40)
    profile = build_profile(journals, history[:10])
    return render_template('chat/chat.html', history=history, profile=profile, lang=lang, title="Ask Madhav · Shlokas • Guidance • Always With You")

@chat_bp.route('/chat/clear', methods=['POST'])
def clear_chat_page():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('auth.login_page'))
    from models.chat_model import clear_for_user
    from services.conversation_manager import get_conversation_manager
    clear_for_user(uid)
    get_conversation_manager().reset_context(uid)
    return redirect(url_for('chat.chat_page'))


