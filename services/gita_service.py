import json
import re
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "gita" / "gita_verses.json"
LEGACY_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "gita.json"

def _load_gita_verses():
    path = DATA_FILE if DATA_FILE.exists() else LEGACY_DATA_FILE
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[GitaService] Error loading verses from {path}: {e}")
        return []

GITA_VERSES = _load_gita_verses()
for _v in GITA_VERSES:
    if "theme" not in _v:
        _v["theme"] = _v.get("concept_or_topic", "General").capitalize()
GITA = GITA_VERSES

def get_verse_in_lang(verse, lang="en"):
    """Returns an enriched view of the verse with active meaning and guidance based on language."""
    if not verse:
        return verse
    v = dict(verse)
    lang = (lang or "en").lower().strip()
    if lang in ["hi", "hindi"]:
        v["active_meaning"] = v.get("translation_hi") or v.get("simple_meaning_hi") or v.get("simple_meaning", "")
        v["active_guidance"] = v.get("simple_meaning_hi") or v.get("translation_hi") or v.get("practical_interpretation", "")
        v["active_lang"] = "hi"
    elif lang in ["hinglish", "roman"]:
        v["active_meaning"] = v.get("translation_hinglish") or v.get("simple_meaning_hinglish") or v.get("simple_meaning", "")
        v["active_guidance"] = v.get("simple_meaning_hinglish") or v.get("translation_hinglish") or v.get("practical_interpretation", "")
        v["active_lang"] = "hinglish"
    else:
        v["active_meaning"] = v.get("translation") or v.get("simple_meaning", "")
        v["active_guidance"] = v.get("practical_interpretation", "")
        v["active_lang"] = "en"

    # Backward compatibility keys
    v["meaning_en"] = v.get("translation") or v.get("simple_meaning", "")
    v["meaning_hi"] = v.get("translation_hi") or v.get("simple_meaning_hi", "")
    v["meaning_hinglish"] = v.get("translation_hinglish") or v.get("simple_meaning_hinglish", "")
    return v

def get_verse_by_reference(reference_str, lang="en"):
    """
    Looks up a verse by explicit chapter and verse reference.
    e.g. '2.47', '2:47', 'Bhagavad Gita 2.47', 'अध्याय 2 श्लोक 47'.
    """
    if not reference_str:
        return None
    match = re.search(r'(\d+)[\.\:\s]+(\d+)', reference_str)
    if not match:
        return None
    ch, vs = int(match.group(1)), int(match.group(2))
    for v in GITA_VERSES:
        if v.get("chapter") == ch and v.get("verse") == vs:
            return get_verse_in_lang(v, lang)
    return None

def should_include_gita(intent, text, context=None):
    """
    Determines if Bhagavad Gita wisdom is genuinely relevant.
    User Rule:
    - 'what are you doing?' -> NO Gita
    - 'how can I become better at cricket?' -> NO Gita
    - 'what is python?' -> NO Gita
    - 'I am scared I will fail my exam' -> Gita may be relevant if spiritual/emotional framing fits
    - 'What does Krishna say about failure?' -> YES Gita
    - 'Explain Bhagavad Gita 2.47' -> YES Gita
    """
    lower = (text or "").lower()

    # Explicit requests for Gita / Krishna
    explicit_markers = [
        "gita", "bhagavad gita", "shloka", "shlok", "krishna", "sanskrit", "verse",
        "गीता", "श्रीकृष्ण", "श्लोक", "कर्म", "अर्जुन", "arjun", "karma yoga"
    ]
    if any(m in lower for m in explicit_markers):
        return True

    # Intent is explicitly a Gita request
    if intent in ["BHAGAVAD_GITA_REQUEST", "gita_question", "gita_shloka"]:
        return True

    # Casual, technical, general questions, career questions, or sports advice NEVER force Gita
    casual_or_tech_indicators = [
        "how are you", "what are you doing", "who are you", "joke", "bored",
        "sports", "cricket", "football", "badminton", "chess",
        "python", "programming", "coding", "software", "computer",
        "web development", "course", "courses", "earning", "earn money",
        "weather", "capital", "math", "physics"
    ]
    if any(re.search(r'\b' + re.escape(w) + r'\b', lower) for w in casual_or_tech_indicators):
        return False

    # Deep emotional struggles where user is seeking spiritual grounding
    if intent in ["EMOTIONAL_SUPPORT", "philosophical_question"]:
        if any(w in lower for w in ["dharma", "purpose", "why me", "soul", "fate", "peace of mind", "inner peace", "detachment", "karma"]):
            return True

    return False

def is_problem_requiring_guidance(text, intent=None, category=None):
    """
    Detects if the user is sharing any mental, physical, social, or emotional problem
    that should be guided with wisdom and a relevant Gita shloka.
    """
    if not text:
        return False
    lower = text.lower()

    # Casual, technical, sports, or career guidance questions are NEVER problem categories
    casual_or_tech = [
        "how are you", "what are you doing", "who are you", "joke", "bored",
        "sports", "cricket", "football", "badminton", "chess",
        "python", "programming", "coding", "software", "computer",
        "web development", "courses for earning", "course for earning", "earning", "earn money",
        "weather", "capital", "math", "physics", "calculate"
    ]
    if any(re.search(r'\b' + re.escape(w) + r'\b', lower) for w in casual_or_tech):
        return False

    problem_words = [
        # Mental / Emotional
        "stress", "depress", "tension", "mental pressure", "anxi", "panic", "overthink",
        "dimag kharab", "udas", "sad", "hopeless", "worthless", "self doubt", "fear",
        "scared", "darr", "afraid", "nervous", "chinta", "burnout", "peace of mind",
        "sukoon nahi", "mann shant nahi", "overwhelm",

        # Physical / Health / Habits / Fatigue
        "exhaust", "fatigue", "tired", "insomnia", "neend nahi", "sleep", "letharg",
        "lazy", "laziness", "aalas", "bad habit", "procrastinat", "restless", "bechain",
        "health", "weakness", "kamzori",

        # Social / Relationships / Loneliness
        "lonel", "akela", "akelapan", "breakup", "fight", "quarrel", "argument",
        "toxic", "betrayal", "nobody loves", "social anxiety", "peer pressure",
        "judged", "dost ne", "parents", "family problem", "relationship",

        # Life / Academic / Failure
        "fail", "failure", "haar gaya", "reject", "rejection", "stuck in life",
        "confused", "no motivation", "demotivat", "give up", "giving up"
    ]
    return any(pw in lower for pw in problem_words)

def search(query="", theme="all", lang="en"):
    items = GITA_VERSES
    if theme and theme != "all":
        items = [x for x in items if x.get("concept_or_topic", "").lower() == theme.lower()]

    if query:
        q = query.lower().strip()
        filtered = []
        for x in items:
            searchable = (
                x.get("concept_or_topic", "") + " " +
                x.get("reference", "") + " " +
                " ".join(x.get("keywords", [])) + " " +
                x.get("simple_meaning", "") + " " +
                x.get("simple_meaning_hi", "") + " " +
                x.get("simple_meaning_hinglish", "") + " " +
                x.get("sanskrit", "") + " " +
                x.get("transliteration", "")
            ).lower()
            if q in searchable:
                filtered.append(x)
        items = filtered

    return [get_verse_in_lang(x, lang) for x in items]

def recommend(text, lang="en"):
    """
    Rule & keyword based verse recommendation.
    Prefers exact chapter/verse lookup if specified, else situation-based.
    Supports Mental, Physical, Social, and Life/Academic challenges.
    """
    ref_match = get_verse_by_reference(text, lang)
    if ref_match:
        return ref_match

    val = (text or "").lower()
    best = None
    best_score = 0

    for item in GITA_VERSES:
        score = sum(1 for k in item.get("keywords", []) if k.lower() in val)
        ref = item.get("reference", "")

        # 1. Mental / Stress / Exam Results / Worry
        if any(w in val for w in ["stress", "tension", "exam", "marks", "result", "chinta", "pariksha", "padhai"]):
            if ref == "Bhagavad Gita 2.47":
                score += 5

        # 2. Mental / Overthinking / Wandering Mind / Anxiety
        if any(w in val for w in ["overthink", "thoughts", "soch", "dimag", "anxiety", "man", "mann", "restless", "bechain"]):
            if ref in ["Bhagavad Gita 6.35", "Bhagavad Gita 6.5", "Bhagavad Gita 6.26"]:
                score += 5

        # 3. Academic / Life Failure & Discouragement
        if any(w in val for w in ["fail", "failure", "haar", "give up", "demotivated", "hopeless", "rejection", "stuck"]):
            if ref in ["Bhagavad Gita 2.3", "Bhagavad Gita 2.48", "Bhagavad Gita 2.40", "Bhagavad Gita 12.18"]:
                score += 4

        # 4. Fear & Anxiety about the Unknown
        if any(w in val for w in ["fear", "darr", "scared", "afraid"]):
            if ref in ["Bhagavad Gita 2.38", "Bhagavad Gita 18.30"]:
                score += 4

        # 5. Anger, Frustration & Irritation
        if any(w in val for w in ["anger", "gussa", "krodh", "irritated", "frustrated"]):
            if ref in ["Bhagavad Gita 2.62", "Bhagavad Gita 2.63"]:
                score += 5

        # 6. Physical / Fatigue / Lifestyle / Sleep / Exhaustion
        if any(w in val for w in ["fatigue", "tired", "exhaust", "sleep", "insomnia", "neend", "thak", "health", "body", "weakness"]):
            if ref in ["Bhagavad Gita 6.16", "Bhagavad Gita 6.17", "Bhagavad Gita 2.14"]:
                score += 5

        # 7. Social / Relationships / Loneliness / Conflict / Betrayal
        if any(w in val for w in ["lonel", "akela", "akelapan", "relationship", "breakup", "fight", "quarrel", "betray", "friend", "parent", "dost", "parivaar"]):
            if ref in ["Bhagavad Gita 12.18", "Bhagavad Gita 12.13", "Bhagavad Gita 6.29"]:
                score += 5

        # 8. Laziness / Procrastination / Self-Mastery
        if any(w in val for w in ["lazy", "laziness", "aalas", "procrastinat", "bad habit", "discipline"]):
            if ref in ["Bhagavad Gita 6.5", "Bhagavad Gita 6.6"]:
                score += 5

        # 9. Peace, Calm, Inner Harmony
        if any(w in val for w in ["peace", "calm", "sukoon", "shanti", "equanimity"]):
            if ref in ["Bhagavad Gita 2.70", "Bhagavad Gita 2.48"]:
                score += 4

        if score > best_score:
            best_score = score
            best = item

    chosen = best if best else (GITA_VERSES[0] if GITA_VERSES else {})
    return get_verse_in_lang(chosen, lang)
