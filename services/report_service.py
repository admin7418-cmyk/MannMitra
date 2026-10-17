from collections import Counter
from datetime import datetime, timedelta


def _value(row, key, default=None):
    if row is None:
        return default
    if hasattr(row, "get"):
        return row.get(key, default)
    try:
        return row[key]
    except (KeyError, IndexError, TypeError):
        return default


def build_summary(journals):
    if not journals:
        return {"total_entries": 0, "positive": 0, "neutral": 0, "low": 0}
    moods = Counter(row["mood"] for row in journals)
    return {"total_entries": len(journals), "positive": moods.get("Positive", 0), "neutral": moods.get("Neutral", 0), "low": moods.get("Low", 0)}


def _score(row):
    try:
        return float(_value(row, "score", 0))
    except (TypeError, ValueError):
        return 0.0


def build_weekly_report(journals, chats, habits, memory, wisdom):
    now = datetime.now()
    cutoff = (now - timedelta(days=7)).isoformat()
    previous_cutoff = (now - timedelta(days=14)).isoformat()
    week = [j for j in journals if _value(j, "created_at", "") >= cutoff]
    previous = [j for j in journals if previous_cutoff <= _value(j, "created_at", "") < cutoff]
    avg = sum(_score(j) for j in week) / len(week) if week else 0
    prev_avg = sum(_score(j) for j in previous) / len(previous) if previous else 0
    delta = avg - prev_avg if previous else 0
    mood_counts = Counter(_value(j, "mood", "Neutral") for j in week)
    main_mood = mood_counts.most_common(1)[0][0] if mood_counts else "No signal yet"

    if not week:
        direction = "Getting started"
        observation = "Add a few reflections this week so MannMitra can build a useful weekly picture."
    elif not previous:
        direction = "Building your baseline"
        observation = "This is your first comparison period. Keep reflecting naturally and a clearer trend will appear next week."
    elif delta > 0.08:
        direction = "Moving upward"
        observation = "Your recent journal tone is more positive than the previous period. Notice which routines or moments may be helping."
    elif delta < -0.08:
        direction = "Needs a little care"
        observation = "Your recent journal tone is lower than the previous period. Consider slowing down, naming one concern, and choosing one manageable next step."
    else:
        direction = "Steady"
        observation = "Your recent mood signal is fairly steady. Small consistent actions can be more useful than trying to change everything at once."

    return {
        "period": f"{(now - timedelta(days=6)).strftime('%d %b')} – {now.strftime('%d %b %Y')}",
        "entries": len(week),
        "average": round(avg, 2),
        "previous_average": round(prev_avg, 2),
        "delta": round(delta, 2),
        "direction": direction,
        "main_mood": main_mood,
        "mood_counts": dict(mood_counts),
        "main_theme": memory.get("dominant_theme", "general").replace("_", " ").title(),
        "observation": observation,
        "habit_completed": memory.get("habit_completed", 0),
        "habit_total": memory.get("habit_total", 0),
        "chat_count": len(chats),
        "wisdom": wisdom,
        "suggestions": [
            "Choose one small priority for the day instead of carrying every task at once.",
            "Write a short reflection when your mind feels crowded; naming the thought can make it easier to handle.",
            "Keep one simple habit consistent this week and review how it affects your mood."
        ]
    }
