import re
from difflib import SequenceMatcher
from services.conversation_memory import resolve_contextual_continuation, is_short_reply
from services.safety_service import needs_human_support

CATEGORY_SAFETY_RISK = "SAFETY_RISK"
CATEGORY_BHAGAVAD_GITA_REQUEST = "BHAGAVAD_GITA_REQUEST"
CATEGORY_GENERAL_QUESTION = "GENERAL_QUESTION"
CATEGORY_CASUAL_CONVERSATION = "CASUAL_CONVERSATION"
CATEGORY_PERSONAL_SHARING = "PERSONAL_SHARING"
CATEGORY_ADVICE_OR_DECISION = "ADVICE_OR_DECISION"
CATEGORY_EMOTIONAL_SUPPORT = "EMOTIONAL_SUPPORT"

CONTRACTIONS = {
    "can't": "cannot", "won't": "will not", "i'm": "i am", "i've": "i have",
    "it's": "it is", "don't": "do not", "doesn't": "does not", "didn't": "did not",
    "you're": "you are", "they're": "they are", "we're": "we are", "cant": "cannot",
    "dont": "do not", "im": "i am", "ive": "i have", "idk": "i do not know",
    "wnat": "want", "sominthing": "something", "somthing": "something"
}

def normalize_text(text):
    if not text:
        return ""
    val = text.lower().strip()
    for c, full in CONTRACTIONS.items():
        val = re.sub(r'\b' + re.escape(c) + r'\b', full, val)
    val = re.sub(r'[^\w\s\u0900-\u097f]', ' ', val)
    return re.sub(r'\s+', ' ', val).strip()

def fuzzy_match(phrase, text, threshold=0.82):
    p_len = len(phrase)
    if p_len < 4:
        return re.search(r'\b' + re.escape(phrase) + r'\b', text) is not None
    words = text.split()
    p_words_count = len(phrase.split())
    for i in range(len(words) - p_words_count + 1):
        window = " ".join(words[i:i + p_words_count])
        if SequenceMatcher(None, phrase, window).ratio() >= threshold:
            return True
    return False

# Comprehensive pattern dictionary for intents
INTENT_PATTERNS = {
    # Casual small talk
    "how_are_you": [
        "how are you", "how r u", "how are you doing", "how do you do", "how are you feeling",
        "how is it going", "hows it going", "are you okay", "how have you been",
        "आप कैसे हैं", "कैसे हो", "कैसी हो", "सब कैसा है", "क्या हाल है", "सब ठीक है",
        "kaise ho", "kaisa hai", "kya haal hai", "kya hal hai", "aap kaise ho", "sab kaisa hai", "sab thik"
    ],
    "what_are_you_doing": [
        "what are you doing", "what r u doing", "what are u doing", "what are you up to",
        "what r you doing", "what are u up to", "what are you busy with", "what's going on",
        "आप क्या कर रहे हैं", "क्या कर रहे हो", "क्या कर रही हो", "क्या चल रहा है", "और बताओ",
        "kya kar rahe ho", "kya kr rhe ho", "kya kar raha hai", "kya chal raha hai", "aur batao"
    ],
    "what_are_you_thinking": [
        "what are you thinking", "what is on your mind",
        "क्या सोच रहे हो", "मन में क्या चल रहा है", "kya soch rahe ho"
    ],
    "life_ambition_big": [
        "want to do something big", "do something big in my life", "do sominthing big in my life",
        "wnat to do sominthing big", "kuch bada karna hai", "life mein kuch bada", "bada aadmi banna hai",
        "zindagi mein kuch bada", "zindagi me kuch bada karna hai", "want to achieve greatness"
    ],
    "tell_joke": [
        "tell me a joke", "tell a joke", "make me laugh", "say something funny",
        "कोई जोक सुनाओ", "मजाक सुनाओ", "कोई चुटकुला", "koi joke sunao", "chutkula sunao"
    ],
    "boredom": [
        "i am bored", "feeling bored", "bore ho raha", "bore ho raha hoon", "bore ho rahi hoon", "bore lag raha hai"
    ],
    "did_you_eat": [
        "did you eat", "have you eaten", "did you have dinner", "did you have lunch",
        "खाना खाया", "खाना खा लिया", "khana khaya", "khana kha liya"
    ],
    "who_are_you": [
        "who are you", "what is your name", "tell me about you", "tum kaun ho", "aap kaun hain", "aapka naam kya hai"
    ],
    "greeting": [
        "hello", "hi", "hey", "good morning", "good evening", "namaste", "pranam", "sup",
        "नमस्ते", "प्रणाम", "नमस्कार", "हेलो", "हाय"
    ],
    "goodbye": [
        "bye", "goodbye", "see you", "alvida", "take care", "good night", "शुभ रात्रि", "अलविदा", "बाय"
    ],
    "thanks": [
        "thank you", "thanks", "dhanyawad", "shukriya", "grateful", "धन्यवाद", "शुक्रिया", "thank u"
    ],
    "friendship": [
        "will you become my friend", "will you be my friend", "can we be friends",
        "be my friend", "are you my friend", "make friends with me", "best friend",
        "क्या आप मेरे दोस्त बनेंगे", "मेरे दोस्त बनोगे", "दोस्त बनोगे", "मित्र बनोगे",
        "kya tum mere dost banoge", "kya aap mere dost banenge", "dost banoge", "mere dost ban jao"
    ],

    # General technical / informational questions
    "technical_question": [
        "what is python", "how does python work", "explain python", "what is coding",
        "what is programming", "what is software", "how does internet work", "what is html"
    ],
    "sports_question": [
        "how can i become good at cricket", "how to play cricket", "achha sports khelna hai",
        "sports advice", "football kaise khele", "cricket batting tips", "sports training",
        "better at cricket", "cricket khelna hai"
    ],

    # Advice & decisions
    "career_advice": [
        "courses for earning", "do some courses for earning", "courses to earn money",
        "which course should i do", "course suggest karo", "earning ke liye course",
        "career guidance", "freelancing course", "web development course", "skill seekhni hai",
        "roadmap", "roadmap batao", "python sikhna", "python seekhna", "coding sikhna",
        "time management", "manage time", "sarkari naukri", "सरकारी नौकरी", "प्राइवेट जॉब",
        "सरकारी नौकरी या प्राइवेट", "sarkari ya private", "career dilemma", "routine kaise"
    ],

    # Personal sharing
    "personal_reflection": [
        "thinking about future", "just thinking about future", "nothing just thinking",
        "future ke baare mein soch raha", "aage kya karu soch raha tha", "aaj ka din thaka dene wala tha"
    ],
    "study_effort": [
        "i studied a lot", "studied for three months", "studied for 3 months", "worked hard for exam",
        "bohot padha tha", "bohot mehnat ki thi", "din raat ek kiya tha"
    ],

    # Emotional support
    "study_stress": [
        "exam tension", "exam stress", "exam anxiety", "terrified of failing", "anxious about my exams",
        "semester exam", "syllabus is huge", "padhai ka tension", "pariksha ki chinta", "marks nahi aa rahe",
        "the result", "my exams", "results tension", "marks ki tension", "परीक्षा", "चिंता", "तनाव", "परीक्षा को लेकर"
    ],
    "anxiety": [
        "i have so much anxiety", "anxious", "panic attack", "heart is racing", "anxiety ho rahi hai",
        "घबराहट", "बेचैनी", "anxious feel ho raha", "bohot darr lag raha hai"
    ],
    "stress": [
        "i am so stressed", "i am stressed", "stress ho rahi hai", "bahut tension hai", "तनाव", "depression", "बहुत तनाव"
    ],
    "happiness": [
        "happy", "happiness", "so happy", "peaceful", "joy", "excited", "peaceful today",
        "feeling good", "wonderful", "प्रसन्न", "खुश", "khush", "sukoon"
    ],
    "sadness": [
        "i am feeling really sad", "sad and hopeless", "heartbroken", "feeling down", "उदासी", "मन उदास है", "bahut udas hoon"
    ],
    "failure": [
        "i failed my exam", "failed my test", "i flunked", "fail ho gaya", "exam mein fail", "असफल हो गया", "i still failed"
    ],
    "overthinking": [
        "stop overthinking", "mind won't stop overthinking", "overthinking every single scenario",
        "dimag shant nahi ho raha", "bahut zyada soch raha hoon", "overthinking band kaise kare", "bohot overthinking",
        "neend nahi aati", "raat ko neend", "so nahi pa raha", "overthinking hoti hai", "can't sleep", "cannot sleep"
    ],
    "loneliness": [
        "i feel so lonely", "nobody cares", "alone in life", "अकेलापन", "akelapan", "koi nahi samajhta"
    ],
    "fear": [
        "scared about my future", "fear of future", "scared of failure", "fear of failing", "bhavishya ka darr", "dar lag raha hai"
    ],
    "relationship_problem": [
        "breakup", "boyfriend broke up", "girlfriend broke up", "fight with best friend", "jhagda ho gaya", "dhokha diya",
        "friend stopped talking", "dost baat nahi kar raha", "friend not talking", "dost naraz hai", "fight with friend", "dost se ladai"
    ],

    # Explicit Gita requests
    "gita_question": [
        "what does bhagavad gita say about", "what does krishna say about", "gita ke anusaar",
        "explain bhagavad gita", "gita 2.47", "bhagavad gita 2.47", "gita shloka", "shlok sunao",
        "bhagavad gita teach about", "bhagavad gita say", "krishna teach", "gita teach", "karma",
        "teach about karma", "teach about"
    ],
    "guidance_next_step": [
        "what should i do now", "what should i do right now", "what should i do", "what do i do now",
        "what is the next step", "ab kya karu", "ab aage kya karein", "how should i move forward", "what can i do right now"
    ]
}

TOPIC_MAPPING = {
    "how_are_you": "casual_chat",
    "what_are_you_doing": "casual_chat",
    "what_are_you_thinking": "casual_chat",
    "life_ambition_big": "ambition_growth",
    "tell_joke": "casual_chat",
    "boredom": "casual_chat",
    "did_you_eat": "casual_chat",
    "who_are_you": "identity",
    "greeting": "casual_chat",
    "goodbye": "casual_chat",
    "thanks": "gratitude",
    "friendship": "friendship",
    "happiness": "emotional_wellness",
    "technical_question": "technical_knowledge",
    "sports_question": "sports_fitness",
    "career_advice": "career_growth",
    "personal_reflection": "future_planning",
    "study_effort": "exams_studies",
    "study_stress": "exams_studies",
    "anxiety": "emotional_wellness",
    "stress": "emotional_wellness",
    "sadness": "emotional_wellness",
    "failure": "exams_studies",
    "overthinking": "mind_control",
    "loneliness": "emotional_wellness",
    "fear": "emotional_wellness",
    "relationship_problem": "relationships_friends",
    "gita_question": "gita_wisdom",
    "guidance_next_step": "practical_solutions"
}

PROBLEM_INTENTS = {
    "study_stress", "stress", "anxiety", "sadness", "failure", "overthinking",
    "fear", "anger", "loneliness", "relationship_problem", "family_problem",
    "sleep_problem", "self_confidence", "career_stress", "study_effort"
}

def is_problem_situation(intent, text=""):
    """Determines whether user is presenting a genuine struggle/problem that calls for emotional support."""
    if intent in PROBLEM_INTENTS:
        return True
    lower = (text or "").lower()
    hindi_problem_words = [
        "चिंता", "तनाव", "परीक्षा", "डर", "उदासी", "परेशान", "विफलता", "घबराहट", "अकेला", "अकेलापन", "क्रोध", "गुस्सा"
    ]
    if any(w in lower for w in hindi_problem_words):
        return True
    problem_words = [
        "stress", "stressed", "tension", "sad", "sadness", "fail", "failed", "failure",
        "exam", "exams", "anxiety", "anxious", "fear", "scared", "afraid", "worry", "worried",
        "darr", "dar", "chinta", "overthink", "overthinking", "breakup", "fight", "insomnia",
        "neend", "lonely", "alone", "pareshan", "gussa", "depression", "depressed", "hopeless",
        "helpless", "struggling", "takleef", "ghabrahat", "heartbroken"
    ]
    return any(re.search(r'\b' + re.escape(w), lower) for w in problem_words)

def classify_intent_category(text, intent, topic, context=None):
    """
    Maps the detected state to one of the 7 Internal Conversation Categories:
    - SAFETY_RISK
    - BHAGAVAD_GITA_REQUEST
    - GENERAL_QUESTION
    - CASUAL_CONVERSATION
    - PERSONAL_SHARING
    - ADVICE_OR_DECISION
    - EMOTIONAL_SUPPORT
    """
    lower = (text or "").lower()

    # 1. Safety Risk
    if needs_human_support(text) or intent == "crisis_or_self_harm":
        return CATEGORY_SAFETY_RISK

    # 2. Explicit Bhagavad Gita Request
    gita_triggers = [
        "what does bhagavad gita say", "what does krishna say", "explain bhagavad gita",
        "gita 2.47", "bhagavad gita 2.47", "gita verse", "bhagavad gita shloka",
        "गीता के अनुसार", "श्लोक का अर्थ"
    ]
    if intent == "gita_question" or any(t in lower for t in gita_triggers) or re.search(r'\b(gita|bhagavad gita)\s+\d+[\.:]\d+\b', lower):
        return CATEGORY_BHAGAVAD_GITA_REQUEST

    # 3. General Information / Technical / Fact Question
    general_q_triggers = [
        "what is python", "what is coding", "what is software", "how does", "what is",
        "explain python", "who built", "what are the rules of"
    ]
    if intent in ["technical_question"] or any(lower.startswith(q) for q in ["what is python", "what is coding", "how does"]):
        return CATEGORY_GENERAL_QUESTION

    # 4. Emotional Support (Exam anxiety, sadness, failure, fear, stress)
    if intent in PROBLEM_INTENTS or is_problem_situation(intent, text):
        return CATEGORY_EMOTIONAL_SUPPORT

    # 5. Advice / Decision / Sports / Career Choice
    advice_triggers = [
        "how can i become good at cricket", "how to play", "achha sports khelna hai",
        "courses for earning", "what course should i do", "what should i choose",
        "career advice", "kya karu", "which one is better", "what should i do",
        "roadmap", "roadmap batao", "manage time", "time management", "sarkari", "सरकारी", "प्राइवेट"
    ]
    if intent in ["sports_question", "career_advice", "life_ambition_big", "guidance_next_step"]:
        return CATEGORY_ADVICE_OR_DECISION
    if any(t in lower for t in advice_triggers):
        return CATEGORY_ADVICE_OR_DECISION

    # 6. Personal Sharing (Opening up about thoughts, efforts, day)
    if intent in ["personal_reflection", "study_effort"] or any(p in lower for p in ["thinking about future", "nothing just thinking", "i studied a lot", "today was"]):
        return CATEGORY_PERSONAL_SHARING

    # 7. Casual Conversation (Default for greetings, small talk, jokes, checks)
    return CATEGORY_CASUAL_CONVERSATION

def detect_intent_and_topic(text, context=None):
    """
    Returns: (intent, topic, confidence, category)
    """
    norm = normalize_text(text)
    if not norm:
        return "general_chat", "general_life", 0.1, CATEGORY_CASUAL_CONVERSATION

    context = context or {}

    # Step 1: Check short reply continuations ("yes", "no", "hmm", "nothing", "actually", etc.)
    short_cat = is_short_reply(text)
    if short_cat:
        res_cont = resolve_contextual_continuation(text, context)
        if res_cont and res_cont[0]:
            _, cont_intent, cont_topic, _ = res_cont
            category = classify_intent_category(text, cont_intent, cont_topic, context)
            return cont_intent, cont_topic, 0.95, category

    # Step 2: Safety check
    if needs_human_support(text):
        return "crisis_or_self_harm", "crisis", 1.0, CATEGORY_SAFETY_RISK

    # Step 3: Pattern matching across intents
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pat in patterns:
            pat_norm = normalize_text(pat)
            if re.search(r'\b' + re.escape(pat_norm) + r'\b', norm):
                score += 5
            elif pat_norm in norm:
                score += 3.0
            elif len(pat_norm.split()) > 1 and fuzzy_match(pat_norm, norm, threshold=0.84):
                score += 2.5
        if score > 0:
            scores[intent] = score

    # Specific overrides for common ambiguities
    if any(w in norm for w in ["something big", "sominthing big", "bada karna", "bada aadmi", "big in my life"]):
        scores["life_ambition_big"] = scores.get("life_ambition_big", 0) + 12

    if any(w in norm for w in ["what are you doing", "what r u doing", "what are u doing", "kya kar rahe ho", "kya chal raha hai"]):
        scores["what_are_you_doing"] = scores.get("what_are_you_doing", 0) + 12

    if any(w in norm for w in ["courses for earning", "course for earning", "do some courses for earning", "earn money", "roadmap", "manage time", "time management", "सरकारी", "sarkari"]):
        scores["career_advice"] = scores.get("career_advice", 0) + 15

    if any(w in norm for w in ["cricket", "sports khelna", "good at cricket"]):
        scores["sports_question"] = scores.get("sports_question", 0) + 15

    if any(w in norm for w in ["what is python", "explain python"]):
        scores["technical_question"] = scores.get("technical_question", 0) + 15

    if any(w in norm for w in ["fear of failure", "gita say about", "explain bhagavad gita", "bhagavad gita 2.47", "gita 2.47"]):
        scores["gita_question"] = scores.get("gita_question", 0) + 15

    if any(w in norm for w in ["fight", "breakup", "broke up", "cheated", "ladai", "jhagda", "friend stopped talking", "dost baat nahi"]):
        scores["relationship_problem"] = scores.get("relationship_problem", 0) + 25
        scores["friendship"] = 0

    if any(w in norm for w in ["neend nahi", "can't sleep", "cannot sleep", "overthinking hoti hai"]):
        scores["overthinking"] = scores.get("overthinking", 0) + 20

    if any(w in norm for w in ["bhagavad gita", "gita", "karma", "krishna"]) and not any(w in norm for w in ["courses", "python", "cricket"]):
        scores["gita_question"] = scores.get("gita_question", 0) + 15

    if any(w in norm for w in ["happy", "happiness", "peaceful today", "so happy"]):
        scores["happiness"] = scores.get("happiness", 0) + 20

    if any(w in norm for w in ["परीक्षा", "तनाव", "चिंता", "डर", "परेशान"]):
        scores["study_stress"] = scores.get("study_stress", 0) + 15

    # Contextual bias from previous conversation turns
    current_topic = context.get("current_topic")
    if current_topic == "exams_studies" and any(w in norm for w in ["result", "marks", "fail", "study", "syllabus", "test"]):
        scores["study_stress"] = scores.get("study_stress", 0) + 4
    if current_topic == "career_growth" and any(w in norm for w in ["freelancing", "job", "money", "earning", "course", "courses"]):
        scores["career_advice"] = scores.get("career_advice", 0) + 4

    if not scores:
        best_intent = "general_chat"
        topic = current_topic or "general_life"
        confidence = 0.3
    else:
        best_intent = max(scores, key=scores.get)
        topic = TOPIC_MAPPING.get(best_intent, current_topic or "general_life")
        confidence = min(round(scores[best_intent] / 6.0, 2), 0.99)

    category = classify_intent_category(text, best_intent, topic, context)
    return best_intent, topic, confidence, category
