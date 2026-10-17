import re
from datetime import datetime

# In-memory session store: user_id -> context dictionary
_ACTIVE_CONTEXTS = {}

PEOPLE_PATTERNS = {
    'parents': ['parents', 'mom', 'mother', 'dad', 'father', 'mummy', 'papa', 'maa'],
    'friends': ['friend', 'friends', 'bestie', 'dost', 'yaar', 'roommate'],
    'teacher': ['teacher', 'professor', 'sir', 'maam', 'prof'],
    'partner': ['girlfriend', 'boyfriend', 'partner', 'gf', 'bf'],
    'family': ['brother', 'sister', 'bhai', 'behen', 'sibling', 'family', 'parivar']
}

PLACE_PATTERNS = {
    'college': ['college', 'university', 'campus', 'uni'],
    'school': ['school', 'coaching', 'tuition'],
    'hostel': ['hostel', 'pg', 'room'],
    'home': ['home', 'house', 'ghar'],
    'library': ['library', 'lab']
}

EVENT_PATTERNS = {
    'exam': ['exam', 'exams', 'test', 'tests', 'finals', 'midterms', 'viva', 'practical', 'board exam', 'pariksha'],
    'result': ['result', 'results', 'marks', 'score', 'grades', 'grade', 'percentage', 'rank'],
    'interview': ['interview', 'placement', 'job interview'],
    'presentation': ['presentation', 'seminar', 'project submission']
}

SHORT_REPLIES = {
    'affirmative': ['yes', 'yeah', 'yep', 'yup', 'haan', 'ha', 'bilkul', 'sahi bola', 'true', 'sure', 'definitely', 'correct', 'right'],
    'negative': ['no', 'nah', 'nope', 'nahi', 'na', 'bilkul nahi', 'not really', 'never'],
    'acknowledgement': ['okay', 'ok', 'theek hai', 'thik hai', 'alright', 'accha', 'achha', 'got it', 'i see'],
    'filler': ['hmm', 'hmmm', 'hmmmm', 'uh', 'um', 'umm'],
    'empty': ['nothing', 'kuch nahi', 'kuch nhi', 'none', 'nothing much'],
    'uncertain': ['i dont know', "i don't know", 'dont know', 'idk', 'pata nahi', 'samajh nahi aa raha', 'not sure', 'confused', 'no idea'],
    'continuation': ['actually', 'actually...', 'basically', 'asliyat mein', 'sach kahun toh'],
    'similarity': ['same', 'same here', 'ditto', 'wahi', 'mere sath bhi']
}

def create_default_context(user_id):
    return {
        "user_id": str(user_id),
        "recent_messages": [],        # list of {role, text, intent, topic, mood, response_id}
        "current_topic": None,
        "current_mood": None,
        "previous_intent": None,
        "last_bot_question": None,
        "last_bot_opening": None,
        "turn_count": 0,
        "mentioned_people": [],
        "mentioned_places": [],
        "mentioned_events": [],
        "recent_response_ids": [],    # IDs of responses used recently
        "effort_duration": None,      # e.g., "3 months", "a lot"
        "failure_acknowledged": False,
        "created_at": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat()
    }

def get_context(user_id):
    from services.conversation_manager import get_conversation_manager
    return get_conversation_manager().get_context(user_id)

def reset_context(user_id):
    from services.conversation_manager import get_conversation_manager
    return get_conversation_manager().reset_context(user_id)

def extract_entities(text, context):
    """Extract mentioned people, places, events, and effort durations from text."""
    lower = text.lower()
    
    for category, words in PEOPLE_PATTERNS.items():
        if any(re.search(r'\b' + re.escape(w) + r'\b', lower) for w in words):
            if category not in context["mentioned_people"]:
                context["mentioned_people"].append(category)

    for category, words in PLACE_PATTERNS.items():
        if any(re.search(r'\b' + re.escape(w) + r'\b', lower) for w in words):
            if category not in context["mentioned_places"]:
                context["mentioned_places"].append(category)

    for category, words in EVENT_PATTERNS.items():
        if any(re.search(r'\b' + re.escape(w) + r'\b', lower) for w in words):
            if category not in context["mentioned_events"]:
                context["mentioned_events"].append(category)

    # Detect effort investment (e.g., "studied for three months", "worked hard for a year")
    effort_match = re.search(r'(?:stud(?:ied|y)|prep(?:ared|aring)|work(?:ed|ing))\s+(?:for\s+)?(\d+\s+(?:months?|weeks?|years?|days?)|three\s+months|two\s+months|a\s+year|bohot\s+padha|bohot\s+mehnat|din\s+raat)', lower)
    if effort_match:
        context["effort_duration"] = effort_match.group(1) if effort_match.groups() else "significant effort"

    if re.search(r'\b(fail(?:ed)?|flunked|kharab\s+gaya|haar\s+gaya|fail\s+ho\s+gaya)\b', lower):
        context["failure_acknowledged"] = True

    return context

def is_short_reply(text):
    clean = re.sub(r'[^\w\s]', '', text.lower()).strip()
    words = clean.split()
    if len(words) <= 3:
        for cat, list_words in SHORT_REPLIES.items():
            if clean in list_words or any(clean == w for w in list_words):
                return cat
    return None

def resolve_contextual_continuation(text, context):
    """
    Resolves whether a short phrase or continuation connects to previous topic.
    Returns: (is_continuation, inferred_intent, inferred_topic, inferred_mood)
    """
    clean = text.strip().lower()
    clean_no_punc = re.sub(r'[^\w\s]', '', clean).strip()
    
    current_topic = context.get("current_topic")
    prev_intent = context.get("previous_intent")
    last_q = (context.get("last_bot_question") or "").lower()

    # Case 1: Specific short answers to Bot's questions
    # E.g. Bot asked: "Is it syllabus, remembering, or result?"
    # User replies: "The result" or "result" or "syllabus"
    if clean_no_punc in ["the result", "result", "results", "marks", "result ki"]:
        return (True, "study_stress", "exams_studies", "anxious")
    if clean_no_punc in ["syllabus", "syllabus completion", "course"]:
        return (True, "study_stress", "exams_studies", "stressed")
    if clean_no_punc in ["remembering", "remembering what ive studied", "forgetting", "yaad nahi rehta"]:
        return (True, "study_stress", "exams_studies", "stressed")
        
    # Case 2: Short answers to "What's making you stressed?"
    # User replies: "My exams" or "exams" or "college" or "parents"
    if clean_no_punc in ["my exams", "exams", "exam", "pariksha", "padhai"]:
        return (True, "study_stress", "exams_studies", "stressed")
    if clean_no_punc in ["career", "future", "job", "placement"]:
        return (True, "career_stress", "career_future", "anxious")
    if clean_no_punc in ["relationship", "friends", "dost", "breakup", "partner"]:
        return (True, "relationship_problem", "relationships_friends", "sad")
    if clean_no_punc in ["family", "parents", "ghar wale"]:
        return (True, "family_problem", "family", "stressed")

    # Case 3: Affirmative ("yes", "haan", "sure") after advice or inquiry
    if clean_no_punc in SHORT_REPLIES['affirmative']:
        if current_topic:
            return (True, "continuation_agree", current_topic, context.get("current_mood", "hopeful"))
        return (True, "general_chat", "general_life", "neutral")

    # Case 4: Negative ("no", "nahi", "nah")
    if clean_no_punc in SHORT_REPLIES['negative']:
        if current_topic:
            return (True, "continuation_disagree", current_topic, context.get("current_mood", "neutral"))
        return (True, "general_chat", "general_life", "neutral")

    # Case 5: Filler / acknowledgement ("hmm", "okay", "theek hai")
    if clean_no_punc in SHORT_REPLIES['filler'] or clean_no_punc in SHORT_REPLIES['acknowledgement']:
        if current_topic:
            return (True, "continuation_pause", current_topic, context.get("current_mood", "neutral"))
        return (True, "general_chat", "general_life", "neutral")

    # Case 6: "nothing" / "kuch nahi"
    if clean_no_punc in SHORT_REPLIES['empty']:
        return (True, "nothing_expressed", current_topic or "general_life", "neutral")

    # Case 7: "actually..." / "actually"
    if clean_no_punc.startswith("actually") or clean_no_punc in SHORT_REPLIES['continuation']:
        return (True, prev_intent or "general_chat", current_topic or "general_life", context.get("current_mood", "neutral"))

    # Case 8: "i don't know" / "pata nahi"
    if clean_no_punc in SHORT_REPLIES['uncertain']:
        return (True, "uncertainty", current_topic or "general_life", "confused")

    # Case 9: Effort continuation ("I studied for three months", "I studied a lot", "bohot mehnat ki thi")
    if re.search(r'\b(studied\s+(?:a\s+lot|hard|so\s+much)|studied\s+for|mehnat\s+ki\s+thi)\b', clean):
        return (True, "study_effort", current_topic or "exams_studies", "disappointed")

    # Case 10: Subsequent failure ("But I still failed", "failed anyway", "fail ho gaya")
    if re.search(r'\b(still\s+failed|still\s+fail|fail\s+ho\s+gaya|passed\s+nahi|failed)\b', clean):
        return (True, "failure", current_topic or "exams_studies", "disappointed")

    # Case 11: "What should I do now?" / "ab kya karu"
    if re.search(r'\b(what\s+should\s+i\s+do|ab\s+kya\s+karu|kya\s+karna\s+chahiye|now\s+what)\b', clean):
        return (True, "guidance_next_step", current_topic or "general_life", "hopeful")

    return (False, None, None, None)

def record_interaction(user_id, user_text, bot_reply, intent, topic, mood, response_id=None, bot_question=None, bot_opening=None):
    """Save turn into active memory context."""
    ctx = get_context(user_id)
    ctx["turn_count"] += 1
    ctx["current_topic"] = topic or ctx.get("current_topic")
    ctx["current_mood"] = mood or ctx.get("current_mood")
    ctx["previous_intent"] = intent
    ctx["last_bot_question"] = bot_question
    ctx["last_bot_opening"] = bot_opening
    ctx["last_active"] = datetime.now().isoformat()

    extract_entities(user_text, ctx)

    if response_id:
        ctx["recent_response_ids"].append(response_id)
        if len(ctx["recent_response_ids"]) > 25:
            ctx["recent_response_ids"] = ctx["recent_response_ids"][-25:]

    ctx["recent_messages"].append({
        "role": "user",
        "text": user_text,
        "intent": intent,
        "topic": topic,
        "mood": mood,
        "timestamp": datetime.now().isoformat()
    })
    ctx["recent_messages"].append({
        "role": "assistant",
        "text": bot_reply,
        "response_id": response_id,
        "timestamp": datetime.now().isoformat()
    })

    # Keep last 20 messages (10 turns) in memory
    if len(ctx["recent_messages"]) > 20:
        ctx["recent_messages"] = ctx["recent_messages"][-20:]

    return ctx
