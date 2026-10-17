import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from services.conversation_memory import resolve_contextual_continuation

_analyzer = SentimentIntensityAnalyzer()

MOOD_LEXICON = {
    "happy": [
        "happy", "glad", "joyful", "great", "wonderful", "delighted", "content", "peaceful",
        "खुश", "प्रसन्न", "आनंद", "अच्छा", "सुखद",
        "khush", "mast", "badhiya", "achha lag raha", "sukoon"
    ],
    "sad": [
        "sad", "down", "unhappy", "depressed", "heartbroken", "crying", "tears", "hopeless", "blue",
        "उदास", "दुखी", "मायूस", "निराश", "रोना",
        "udas", "dukhi", "rona aa raha", "mayus", "mann bhari"
    ],
    "stressed": [
        "stressed", "stress", "pressure", "overwhelmed", "burdened", "exhausted", "burnout",
        "तनाव", "दबाव", "बोझ", "थकावट",
        "tension", "bohot load", "pressure", "dimag bhari", "pareshan"
    ],
    "anxious": [
        "anxious", "anxiety", "nervous", "jittery", "panic", "restless", "shaking", "uneasy",
        "चिंता", "घबराहट", "बेचैनी", "व्याकुल",
        "ghabrahat", "bechaini", "chinta", "nervous", "dhak dhak"
    ],
    "angry": [
        "angry", "mad", "furious", "annoyed", "irritated", "pissed", "frustrated", "resentful",
        "गुस्सा", "क्रोध", "चिढ़", "नाराज",
        "gussa", "bohot gussa", "chidh", "frustrate", "dimag kharab"
    ],
    "lonely": [
        "lonely", "alone", "isolated", "left out", "abandoned", "empty", "no one",
        "अकेला", "अकेलापन", "सुनसान", "कोई नहीं",
        "akela", "akelapan", "koi nahi hai", "alone feel"
    ],
    "confused": [
        "confused", "lost", "doubtful", "unclear", "puzzled", "indecisive", "dilemma",
        "उलझन", "असमंजस", "भ्रम", "समझ नहीं आ रहा",
        "confused", "samajh nahi aa raha", "kya karu", "uljhan", "pata nahi"
    ],
    "hopeful": [
        "hopeful", "optimistic", "looking forward", "better", "improving", "positive", "faith",
        "आशा", "उम्मीद", "भरोसा", "सकारात्मक",
        "umeed", "hope", "bharosa", "accha hoga", "positive"
    ],
    "excited": [
        "excited", "thrilled", "can't wait", "pumped", "eager", "enthusiastic",
        "उत्साहित", "रोमांचित", "उत्सुक",
        "excited", "bohot maza", "utsah", "josh"
    ],
    "disappointed": [
        "disappointed", "let down", "failed", "flunked", "waste", "regret", "ruined", "lost",
        "निराश", "विफल", "पछतावा", "हार गया",
        "disappoint", "fail ho gaya", "haar gaya", "afsos", "sab bekar"
    ],
    "fearful": [
        "scared", "afraid", "terrified", "fear", "dread", "frightened",
        "डर", "भय", "भयभीत", "डर लग रहा",
        "darr", "dar lag raha", "khauf", "scared"
    ],
    "neutral": [
        "okay", "ok", "fine", "alright", "normal", "nothing special",
        "ठीक", "सामान्य", "कुछ खास नहीं",
        "theek", "chalega", "thik hai", "normal"
    ]
}

INTENT_MOOD_DEFAULTS = {
    "sadness": "sad",
    "stress": "stressed",
    "anxiety": "anxious",
    "loneliness": "lonely",
    "anger": "angry",
    "fear": "fearful",
    "study_stress": "stressed",
    "career_stress": "anxious",
    "failure": "disappointed",
    "success": "excited",
    "happiness": "happy",
    "overthinking": "anxious",
    "self_confidence": "disappointed",
    "greeting": "neutral",
    "goodbye": "neutral",
    "thanks": "happy",
    "friendship": "hopeful",
    "motivation": "hopeful"
}

def detect_mood(text, intent=None, context=None):
    """
    Detects user's emotional state out of the 12 target moods:
    happy, sad, stressed, anxious, angry, lonely, confused, hopeful,
    neutral, excited, disappointed, fearful.
    Returns: (mood, confidence, polarity_score)
    """
    context = context or {}
    clean = (text or "").lower().strip()

    # Step 1: Check contextual continuation
    is_cont, c_intent, c_topic, c_mood = resolve_contextual_continuation(text, context)
    if is_cont and c_mood:
        return c_mood, 0.9, -0.2

    # Step 2: VADER polarity score
    polarity = _analyzer.polarity_scores(text)["compound"]

    # Step 3: Match against emotion lexicon
    scores = {}
    for mood, keywords in MOOD_LEXICON.items():
        score = 0
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', clean):
                score += 3
            elif kw in clean:
                score += 1.5
        if score > 0:
            scores[mood] = score

    # Step 4: Intent synergy
    if intent in INTENT_MOOD_DEFAULTS:
        default_mood = INTENT_MOOD_DEFAULTS[intent]
        scores[default_mood] = scores.get(default_mood, 0) + 2.5

    # Step 5: Resolve
    if scores:
        best_mood = max(scores, key=scores.get)
        confidence = min(round(scores[best_mood] / 5.0, 2), 0.99)
        return best_mood, confidence, polarity

    # Polarity-based fallback
    if polarity >= 0.4:
        return "happy", 0.6, polarity
    elif polarity <= -0.4:
        return "sad", 0.6, polarity
    elif polarity < -0.15:
        return "stressed", 0.5, polarity

    return "neutral", 0.4, polarity
