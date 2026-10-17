from flask import Blueprint, request, jsonify, session
from datetime import datetime
from services.chatbot_service import get_chatbot_service
from services.conversation_manager import get_conversation_manager
from models.chat_model import save, recent

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/v2/chat')

def get_current_user_id():
    return session.get('user_id') or "anonymous_user"

@chatbot_bp.post('')
@chatbot_bp.post('/')
def send_chat_message():
    uid = get_current_user_id()
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    lang = data.get('language') or session.get('lang', 'en')
    session['lang'] = lang

    service = get_chatbot_service()
    result = service.process_message(message, user_id=uid, explicit_lang=lang)

    gita = result.get('gita') or {}
    try:
        save(uid, message, result['reply'], datetime.now().isoformat(),
             result.get('intent', 'general_chat'), gita.get('reference', ''), language=lang)
    except Exception:
        pass

    return jsonify(result)

@chatbot_bp.get('/history')
def get_chat_history():
    uid = get_current_user_id()
    conv_mgr = get_conversation_manager()
    history = conv_mgr.get_history(uid)
    return jsonify({'history': history})

@chatbot_bp.post('/reset')
def reset_conversation():
    uid = get_current_user_id()
    conv_mgr = get_conversation_manager()
    conv_mgr.reset_context(uid)
    return jsonify({'status': 'reset_successful', 'user_id': uid})

@chatbot_bp.post('/feedback')
def submit_response_feedback():
    uid = get_current_user_id()
    data = request.get_json(silent=True) or {}
    response_id = data.get('response_id', '')
    rating = int(data.get('rating', 1))  # 1 for helpful, -1 for unhelpful
    comment = (data.get('comment') or '').strip()
    category = data.get('category', '')
    intent = data.get('intent', '')
    theme_id = data.get('theme_id', '')

    from services.memory_learning_service import get_memory_learning_service
    learning_svc = get_memory_learning_service()
    result = learning_svc.record_feedback(
        user_id=uid,
        response_id=response_id,
        rating=rating,
        comment=comment,
        category=category,
        intent=intent,
        theme_id=theme_id
    )
    return jsonify(result)

@chatbot_bp.get('/memory')
def get_user_learned_memory():
    uid = get_current_user_id()
    from services.memory_learning_service import get_memory_learning_service
    learning_svc = get_memory_learning_service()
    memory = learning_svc.get_user_memory(uid)
    return jsonify({'user_id': uid, 'memory': memory})

@chatbot_bp.post('/memory/clear')
def clear_user_learned_memory():
    uid = get_current_user_id()
    from services.memory_learning_service import get_memory_learning_service
    learning_svc = get_memory_learning_service()
    learning_svc.clear_user_memory(uid)
    return jsonify({'status': 'memory_cleared_successfully', 'user_id': uid})
