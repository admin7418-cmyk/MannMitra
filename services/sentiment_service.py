from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

def analyze(text):
    score = _analyzer.polarity_scores(text)["compound"]
    if score >= 0.35:
        mood = "Positive"
    elif score <= -0.35:
        mood = "Low"
    else:
        mood = "Neutral"
    return score, mood
