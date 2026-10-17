from flask import Blueprint, request, jsonify, session
from services.sentiment_service import analyze
from services.chat_service import generate_reply
from models.chat_model import save, recent
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

def logged(): return session.get('user_id')

@api_bp.post('/analyze')
def analyze_api():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    score, mood = analyze(text)
    return jsonify({'score': score, 'mood': mood})

@api_bp.post('/chat')
def chat_api():
    uid = logged()
    if not uid:
        return jsonify({'error': 'Login required'}), 401
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    lang = data.get('language') or session.get('lang', 'en')
    session['lang'] = lang

    result = generate_reply(message, recent(uid, 10), lang=lang, user_id=uid)
    gita = result.get('gita') or {}
    save(uid, message, result['reply'], datetime.now().isoformat(),
         result.get('type', 'friendly'), gita.get('reference', ''), language=lang)
    return jsonify(result)

@api_bp.post('/chat/clear')
def clear_chat_api():
    uid = logged()
    if not uid:
        return jsonify({'error': 'Login required'}), 401
    from models.chat_model import clear_for_user
    from services.conversation_manager import get_conversation_manager
    clear_for_user(uid)
    get_conversation_manager().reset_context(uid)
    return jsonify({'success': True, 'message': 'Conversation cleared successfully'})

@api_bp.post('/set_language')
def set_language_api():
    data = request.get_json(silent=True) or {}
    lang = (data.get('lang') or 'en').lower().strip()
    if lang in ['en', 'hi', 'hinglish']:
        session['lang'] = lang
        return jsonify({'success': True, 'lang': lang})
    return jsonify({'error': 'Invalid language'}), 400


