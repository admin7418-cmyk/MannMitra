import re
import math
from difflib import SequenceMatcher

def normalize_text(text):
    """
    Cleans and normalizes text for NLP processing across English, Hindi, and Hinglish.
    Preserves Devanagari characters, alphanumeric characters, and basic punctuation.
    """
    if not text:
        return ""
    # Lowercase
    s = text.lower().strip()
    # Replace multiple whitespace
    s = re.sub(r'[\s\t\n]+', ' ', s)
    return s

def clean_for_matching(text):
    """Removes all punctuation and symbols for clean token matching."""
    s = normalize_text(text)
    # Remove punctuation except alphanumeric and Devanagari Unicode range
    s = re.sub(r'[^\w\s\u0900-\u097F]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def compute_text_similarity(text1, text2):
    """Computes normalized string similarity ratio between two texts."""
    if not text1 or not text2:
        return 0.0
    c1 = clean_for_matching(text1)
    c2 = clean_for_matching(text2)
    if not c1 or not c2:
        return 0.0
    return SequenceMatcher(None, c1, c2).ratio()

def extract_ngrams(tokens, n=2):
    """Generates word n-grams from a list of tokens."""
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def cosine_similarity(vec1, vec2):
    """Computes cosine similarity between two numeric vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
