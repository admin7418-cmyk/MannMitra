import re
from datetime import datetime

_ACTIVE_CONTEXTS = {}

class ConversationManager:
    def __init__(self, max_history_window=8):
        self.max_history_window = max_history_window

    def get_context(self, user_id):
        uid = str(user_id or "anonymous")
        if uid not in _ACTIVE_CONTEXTS:
            _ACTIVE_CONTEXTS[uid] = self._create_default_context(uid)

        try:
            from services.memory_learning_service import get_memory_learning_service
            _ACTIVE_CONTEXTS[uid]["user_memory"] = get_memory_learning_service().get_user_memory(uid)
        except Exception:
            pass

        return _ACTIVE_CONTEXTS[uid]

    def reset_context(self, user_id):
        uid = str(user_id or "anonymous")
        _ACTIVE_CONTEXTS[uid] = self._create_default_context(uid)
        return _ACTIVE_CONTEXTS[uid]

    def _create_default_context(self, user_id):
        return {
            "user_id": str(user_id),
            "recent_messages": [],
            "current_topic": None,
            "current_mood": None,
            "previous_intent": None,
            "previous_category": None,
            "last_bot_question": None,
            "last_bot_opening": None,
            "turn_count": 0,
            "mentioned_subjects": [],     # e.g., ["web development", "cricket", "python"]
            "mentioned_people": [],
            "mentioned_places": [],
            "mentioned_events": [],
            "recent_response_ids": [],
            "effort_duration": None,
            "failure_acknowledged": False,
            "last_active": datetime.now().isoformat()
        }

    def resolve_coreference(self, text, context):
        """
        Resolves implicit pronouns or short continuations like 'for freelancing',
        'the result', 'in cricket' using recent subject tracking.
        """
        lower = (text or "").lower().strip()
        recent_subjects = context.get("mentioned_subjects", [])
        last_subject = recent_subjects[-1] if recent_subjects else None

        # Example: 'for freelancing' when last subject was 'web development' or 'course'
        if lower.startswith("for freelancing") or lower == "freelancing":
            return f"{last_subject or 'course'} for freelancing"
        if lower.startswith("for a job") or lower == "job":
            return f"{last_subject or 'career'} for a job"
        if lower in ["the result", "result", "results", "marks"]:
            return f"exam results regarding {context.get('current_topic', 'studies')}"

        return text

    def record_turn(self, user_id, user_text, bot_reply, intent=None, category=None,
                    topic=None, mood=None, response_id=None, bot_question=None, bot_opening=None):
        ctx = self.get_context(user_id)
        ctx["turn_count"] += 1
        ctx["last_active"] = datetime.now().isoformat()

        if intent:
            ctx["previous_intent"] = intent
        if category:
            ctx["previous_category"] = category
        if topic:
            ctx["current_topic"] = topic
        if mood:
            ctx["current_mood"] = mood
        if bot_question:
            ctx["last_bot_question"] = bot_question
        if bot_opening:
            ctx["last_bot_opening"] = bot_opening

        if response_id:
            ctx["recent_response_ids"].append(response_id)
            if len(ctx["recent_response_ids"]) > 25:
                ctx["recent_response_ids"].pop(0)

        # Extract subjects
        self._extract_entities_and_subjects(user_text, ctx)

        # Append to sliding history
        ctx["recent_messages"].append({
            "role": "user",
            "text": user_text,
            "intent": intent,
            "category": category,
            "time": datetime.now().strftime("%H:%M")
        })
        ctx["recent_messages"].append({
            "role": "assistant",
            "text": bot_reply,
            "response_id": response_id,
            "time": datetime.now().strftime("%H:%M")
        })

        # Trim to window limit
        max_items = self.max_history_window * 2
        if len(ctx["recent_messages"]) > max_items:
            ctx["recent_messages"] = ctx["recent_messages"][-max_items:]

        return ctx

    def get_history(self, user_id, max_turns=6):
        ctx = self.get_context(user_id)
        return ctx["recent_messages"][-max_turns*2:]

    def _extract_entities_and_subjects(self, text, ctx):
        lower = text.lower()
        subject_triggers = [
            "web development", "python", "programming", "coding", "cricket", "sports",
            "exam", "exams", "interview", "freelancing", "job", "career", "math",
            "football", "semester", "course", "courses"
        ]
        for sub in subject_triggers:
            if re.search(r'\b' + re.escape(sub) + r'\b', lower):
                if sub not in ctx["mentioned_subjects"]:
                    ctx["mentioned_subjects"].append(sub)

        if re.search(r'\b(fail(?:ed)?|flunked|kharab gaya|fail ho gaya)\b', lower):
            ctx["failure_acknowledged"] = True

_mgr_singleton = None

def get_conversation_manager():
    global _mgr_singleton
    if _mgr_singleton is None:
        _mgr_singleton = ConversationManager()
    return _mgr_singleton
