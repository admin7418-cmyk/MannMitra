import re
from services.safety_service import needs_human_support, response as get_safety_response
from services.conversation_manager import get_conversation_manager
from services.intent_service import detect_intent_and_topic, CATEGORY_SAFETY_RISK
from services.emotion_service import detect_mood
from services.response_manager import get_response_manager
from services.response_validator import get_response_validator
from services.memory_learning_service import get_memory_learning_service

def detect_language(text, explicit_lang=None):
    if explicit_lang and explicit_lang in ['en', 'hi', 'hinglish']:
        return explicit_lang
    if not text:
        return 'en'
    if any('\u0900' <= char <= '\u097f' for char in text):
        return 'hi'
    hinglish_words = ['hai', 'hain', 'mein', 'mera', 'meri', 'kya', 'kaise', 'karo', 'mujhe', 'kuch', 'yaar', 'dost', 'nahi', 'bohot', 'ho', 'batao', 'kar', 'raha', 'rahe']
    lower_words = text.lower().split()
    if sum(1 for w in lower_words if w in hinglish_words) >= 2:
        return 'hinglish'
    return 'en'

class ChatbotService:
    def __init__(self):
        self.conv_manager = get_conversation_manager()
        self.response_manager = get_response_manager()
        self.validator = get_response_validator()
        self.learning_service = get_memory_learning_service()

    def process_message(self, message, user_id=None, explicit_lang=None):
        message = (message or "").strip()
        user_id = str(user_id or "default_user")
        context = self.conv_manager.get_context(user_id)

        # Step 1: Detect language
        lang = detect_language(message, explicit_lang)

        # Step 2: Safety Layer pre-check (Priority 1)
        if needs_human_support(message):
            crisis_reply = get_safety_response(lang, variant_idx=context["turn_count"])
            self.conv_manager.record_turn(
                user_id=user_id,
                user_text=message,
                bot_reply=crisis_reply,
                intent="crisis_or_self_harm",
                category=CATEGORY_SAFETY_RISK,
                topic="crisis",
                mood="sad",
                response_id="crisis_safety_01"
            )
            return {
                "reply": crisis_reply,
                "gita": None,
                "intent": "crisis_or_self_harm",
                "topic": "crisis",
                "mood": "sad",
                "score": -1.0,
                "language": lang,
                "type": "safety",
                "category": CATEGORY_SAFETY_RISK
            }

        # Step 3: Resolve implicit pronouns or continuations using recent conversation context
        resolved_message = self.conv_manager.resolve_coreference(message, context)

        # Step 4: Intent & Category Classification
        intent, topic, confidence, category = detect_intent_and_topic(resolved_message, context)

        # Step 5: Mood & Emotion Detection
        mood, mood_confidence, polarity_score = detect_mood(resolved_message, intent, context)

        # Step 6: Deterministic Response Generation via ResponseManager
        resp_data = self.response_manager.generate_response(
            user_text=resolved_message,
            category=category,
            intent=intent,
            topic=topic,
            mood=mood,
            context=context,
            lang=lang
        )

        reply_text = resp_data.get("reply", "")
        gita_data = resp_data.get("gita")
        res_type = resp_data.get("type", intent)

        # Step 7: Response Validation (10-Point Quality Gate)
        is_valid, val_reason, sanitized_reply = self.validator.validate(
            reply_text=reply_text,
            user_text=message,
            category=category,
            intent=intent,
            context=context,
            gita_verse=gita_data
        )

        if is_valid and sanitized_reply:
            reply_text = sanitized_reply
        elif not is_valid:
            # Fallback to safe friendly acknowledgement
            if lang == "hi":
                reply_text = "मैं आपकी बात समझ रहा हूँ मेरे मित्र। आप इसके बारे में थोड़ा और विस्तार से बताएं।"
            elif lang == "hinglish":
                reply_text = "Main sun raha hoon dost, thoda aur batao is baare mein."
            else:
                reply_text = "I am listening closely, my friend. Tell me a bit more about what is on your mind."

        # Step 8: Save Turn in Conversation Memory
        resp_id = f"{category}_{intent}_{context['turn_count']}"
        self.conv_manager.record_turn(
            user_id=user_id,
            user_text=message,
            bot_reply=reply_text,
            intent=intent,
            category=category,
            topic=topic,
            mood=mood,
            response_id=resp_id
        )

        # Step 9: Extract & Update Local Learnings (Long-Term Memory)
        learned_data = {}
        try:
            learned_data = self.learning_service.extract_and_update_learnings(
                user_id=user_id,
                user_text=message,
                bot_reply=reply_text,
                intent=intent,
                category=category,
                topic=topic
            )
        except Exception:
            pass

        return {
            "reply": reply_text,
            "gita": gita_data,
            "intent": intent,
            "topic": topic,
            "mood": mood,
            "score": polarity_score,
            "language": lang,
            "type": res_type,
            "category": category,
            "response_id": resp_id,
            "learned_memory": {
                "name": learned_data.get("name", ""),
                "career_interest": learned_data.get("career_interest", ""),
                "primary_goal": learned_data.get("primary_goal", ""),
                "known_concerns": learned_data.get("known_concerns", []),
                "interaction_count": learned_data.get("interaction_count", 0)
            }
        }

_service_instance = None

def get_chatbot_service():
    global _service_instance
    if _service_instance is None:
        _service_instance = ChatbotService()
    return _service_instance
