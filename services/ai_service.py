from collections import Counter
from services.sentiment_service import analyze
from services.gita_service import recommend
from services.safety_service import needs_human_support, response

THEMES = {
    'study': ['study','exam','college','assignment','marks','result','revision','subject'],
    'stress': ['stress','stressed','pressure','tension','overload'],
    'overthinking': ['overthink','overthinking','thoughts','confused','confusion'],
    'motivation': ['motivation','lazy','discipline','focus','procrastinate'],
    'fear': ['fear','scared','worried','worry','nervous'],
    'anger': ['angry','anger','irritated','frustrated'],
    'loneliness': ['alone','lonely','isolated'],
}

def detect_theme(text):
    value = (text or '').lower()
    scores = {theme: sum(1 for word in words if word in value) for theme, words in THEMES.items()}
    best = max(scores, key=scores.get) if scores else 'general'
    return best if scores.get(best, 0) else 'general'

def build_profile(journals, chats=None):
    journals = journals or []
    chats = chats or []
    mood_counts = Counter(str(j['mood']) for j in journals)
    themes = Counter(detect_theme(str(j['body'])) for j in journals)
    avg = round(sum(float(j['score']) for j in journals) / len(journals), 2) if journals else 0
    recent_text = ' '.join(str(j['body']) for j in journals[:5])
    focus = themes.most_common(1)[0][0] if themes else 'general'
    return {
        'avg_score': avg,
        'dominant_mood': mood_counts.most_common(1)[0][0] if mood_counts else 'No data',
        'dominant_theme': focus,
        'theme_counts': dict(themes),
        'journal_count': len(journals),
        'chat_count': len(chats),
        'recent_text': recent_text[:1500],
    }

def personalized_insight(profile):
    if not profile['journal_count']:
        return 'Start with one honest reflection today. MannMitra will gradually learn your reflection patterns.'
    theme = profile['dominant_theme']
    mood = profile['dominant_mood']
    if theme == 'study':
        return 'Your recent reflections often mention studies. Try focusing on one small task at a time instead of solving the whole workload together.'
    if theme == 'overthinking':
        return 'Overthinking appears often in your recent reflections. Writing the exact next action can turn a vague thought into something manageable.'
    if theme == 'motivation':
        return 'You have been thinking about motivation and discipline. A small repeatable routine is more useful than waiting for perfect motivation.'
    if mood == 'Positive':
        return 'Your recent reflections show a positive tone. Notice what is working and keep one small habit consistent.'
    if mood == 'Low':
        return 'Your recent reflections have a lower tone. Give yourself a gentle check-in and consider talking to someone you trust if things feel difficult.'
    return 'Keep using your journal honestly. Over time, your mood and theme patterns can become useful self-reflection signals.'

def generate_ai_reply(message, journals, history, lang='en', user_id=None):
    from services.chat_service import generate_reply
    profile = build_profile(journals, history)
    chat_result = generate_reply(message, history, lang=lang, user_id=user_id)
    chat_result['profile'] = profile
    chat_result['theme'] = detect_theme(message)
    return chat_result
