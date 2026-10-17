from collections import Counter
from datetime import datetime, timedelta
from services.ai_service import detect_theme


def _value(item, key, default=None):
    """Read a field from Mongo dicts, sqlite3.Row objects, or normal objects."""
    if item is None:
        return default
    if hasattr(item, "get"):
        return item.get(key, default)
    try:
        return item[key]
    except (KeyError, IndexError, TypeError):
        return default


def _dt(value):
    try:
        return datetime.fromisoformat(str(value).replace('Z', ''))
    except Exception:
        return None


def _number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_memory(journals, chats=None, habits=None):
    journals = journals or []
    chats = chats or []
    habits = habits or []
    themes = Counter()
    moods = Counter()

    for item in journals:
        body = str(_value(item, 'body', ''))
        themes[detect_theme(body)] += 1
        moods[str(_value(item, 'mood', 'Neutral'))] += 1

    now = datetime.now()
    recent = []
    older = []
    for journal in journals:
        created = _dt(_value(journal, 'created_at'))
        if not created:
            continue
        if created >= now - timedelta(days=7):
            recent.append(journal)
        elif now - timedelta(days=14) <= created < now - timedelta(days=7):
            older.append(journal)

    recent_avg = round(sum(_number(_value(j, 'score', 0)) for j in recent) / len(recent), 2) if recent else 0
    older_avg = round(sum(_number(_value(j, 'score', 0)) for j in older) / len(older), 2) if older else 0

    trend = 'stable'
    if recent and older:
        if recent_avg > older_avg + 0.12:
            trend = 'improving'
        elif recent_avg < older_avg - 0.12:
            trend = 'needs_attention'
    elif recent:
        trend = 'new_pattern'

    recurring = themes.most_common(3)
    completed = sum(int(_number(_value(h, 'completed', 0))) for h in habits)

    return {
        'total_reflections': len(journals),
        'total_chats': len(chats),
        'dominant_theme': recurring[0][0] if recurring else 'general',
        'recurring_themes': recurring,
        'dominant_mood': moods.most_common(1)[0][0] if moods else 'No data',
        'mood_counts': dict(moods),
        'recent_average': recent_avg,
        'previous_average': older_avg,
        'trend': trend,
        'habit_total': len(habits),
        'habit_completed': completed,
    }


def get_suggestions(memory):
    theme = memory['dominant_theme']
    suggestions = {
        'study': ['Pick one study task for the next 25 minutes.', 'Write down what is pending instead of keeping it all in your head.'],
        'stress': ['Take a short pause before the next task.', 'Separate what you can control today from what can wait.'],
        'overthinking': ['Write the exact thought that keeps repeating.', 'Choose one small action you can take now.'],
        'motivation': ['Use a tiny repeatable routine rather than waiting for motivation.', 'Celebrate completion of small tasks.'],
        'fear': ['Name the specific thing you are worried about.', 'Focus on the next controllable step.'],
        'anger': ['Pause before reacting to the situation.', 'Write what happened and what response would help you later.'],
        'loneliness': ['Reach out to someone you trust for a simple conversation.', 'Use journaling to describe what kind of support would feel useful.'],
        'general': ['Write one honest reflection today.', 'Notice one thing that went a little better than expected.'],
    }
    result = list(suggestions.get(theme, suggestions['general']))
    if memory['trend'] == 'needs_attention':
        result.append('Your recent mood tone is lower than the previous period; consider a gentle check-in with someone you trust if this continues.')
    return result
