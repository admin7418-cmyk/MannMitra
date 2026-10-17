import json
from pathlib import Path
from services.embedding_service import get_embedding_service
from services.gita_service import GITA_VERSES, get_verse_in_lang, get_verse_by_reference, should_include_gita

class GitaRetrievalService:
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self._index = []
        self._build_index()

    def _build_index(self):
        self._index = []
        for verse in GITA_VERSES:
            # Build rich document string representing the verse concepts
            doc = (
                f"{verse.get('reference', '')} "
                f"concept: {verse.get('concept_or_topic', '')} "
                f"keywords: {' '.join(verse.get('keywords', []))} "
                f"situations: {' '.join(verse.get('situations', []))} "
                f"meaning: {verse.get('translation', '')} "
                f"practical: {verse.get('practical_interpretation', '')}"
            )
            vec = self.embedding_service.embed_text(doc)
            self._index.append({
                "verse": verse,
                "vector": vec,
                "reference": verse.get("reference", "")
            })

    def retrieve(self, query, intent=None, lang="en", threshold=0.32, force=False):
        """
        Retrieves the most semantically relevant Bhagavad Gita verse.
        Returns: (verse_dict or None, similarity_score)
        """
        if not query or not query.strip():
            return None, 0.0

        # Step 1: Check for explicit chapter/verse reference (e.g., '2.47', 'Bhagavad Gita 2.47')
        direct_verse = get_verse_by_reference(query, lang=lang)
        if direct_verse:
            return direct_verse, 1.0

        # Step 2: Check relevance unless forced
        if not force and not should_include_gita(intent, query):
            return None, 0.0

        # Step 3: Semantic embedding search
        q_vec = self.embedding_service.embed_text(query)
        best_verse = None
        best_score = -1.0

        for item in self._index:
            score = self.embedding_service.compute_vector_similarity(q_vec, item["vector"])
            if score > best_score:
                best_score = score
                best_verse = item["verse"]

        # Only return if similarity meets the threshold
        if best_verse and (best_score >= threshold or force):
            return get_verse_in_lang(best_verse, lang=lang), round(best_score, 3)

        return None, round(best_score, 3)

_retrieval_instance = None

def get_retrieval_service():
    global _retrieval_instance
    if _retrieval_instance is None:
        _retrieval_instance = GitaRetrievalService()
    return _retrieval_instance
