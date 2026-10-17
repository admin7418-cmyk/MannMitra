import re
from difflib import SequenceMatcher
from utils.text_utils import clean_for_matching
from services.embedding_service import get_embedding_service

BANNED_REPETITIVE_INTROS = [
    r'i am your friend madhav\b\.?',
    r'i am always here for you\b\.?',
    r'how are your mind and heart feeling\b\??',
    r'it is wonderful to connect with you\b\.?',
    r'i am madhav\b\.?',
    r'main aapka dost madhav hoon\b\.?',
    r'main madhav hoon\b\.?'
]

class RepetitionService:
    def __init__(self, similarity_threshold=0.68):
        self.similarity_threshold = similarity_threshold
        self.embedding_service = get_embedding_service()

    def clean_redundant_intros(self, text, turn_count=0):
        """
        Removes repetitive self-introductions if the conversation is already in progress.
        """
        if not text:
            return ""
        s = text
        if turn_count > 1:
            for pattern in BANNED_REPETITIVE_INTROS:
                s = re.sub(pattern, '', s, flags=re.IGNORECASE).strip()
                # Clean leading punctuation or spaces left over
                s = re.sub(r'^[,\.\-\s]+', '', s).strip()
        return s

    def compute_similarity(self, text1, text2):
        """Computes combined textual and semantic similarity."""
        if not text1 or not text2:
            return 0.0
        # Textual surface similarity
        c1 = clean_for_matching(text1)
        c2 = clean_for_matching(text2)
        text_sim = SequenceMatcher(None, c1, c2).ratio()
        if text_sim > 0.85:
            return text_sim

        # Embedding semantic similarity
        embed_sim = self.embedding_service.compute_similarity(text1, text2)
        return max(text_sim, embed_sim)

    def is_too_similar(self, candidate_text, recent_texts, threshold=None):
        """
        Checks whether candidate_text is overly similar to any recent bot responses.
        """
        if not candidate_text or not recent_texts:
            return False, 0.0, None

        th = threshold or self.similarity_threshold
        cand_clean = clean_for_matching(candidate_text)

        for prev in recent_texts:
            if not prev:
                continue
            prev_clean = clean_for_matching(prev)
            if cand_clean == prev_clean:
                return True, 1.0, prev

            sim = self.compute_similarity(candidate_text, prev)
            if sim >= th:
                return True, sim, prev

        return False, 0.0, None

_repetition_singleton = None

def get_repetition_service():
    global _repetition_singleton
    if _repetition_singleton is None:
        _repetition_singleton = RepetitionService()
    return _repetition_singleton
