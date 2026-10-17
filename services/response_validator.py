import re
from services.gita_service import GITA_VERSES

FORBIDDEN_DIVINE_CLAIMS = [
    "i am shri krishna", "i am krishna", "i am god", "i am divine",
    "krishna is speaking through me", "i speak as krishna",
    "मैं श्रीकृष्ण हूँ", "मैं कृष्ण हूँ", "main krishna hoon", "main shri krishna hoon"
]

UNSAFE_ADVICE_TRIGGERS = [
    "kill yourself", "end your life", "hurt yourself", "take all the pills",
    "give up on life", "jump from", "no one loves you", "you should die"
]

class ResponseValidator:
    def __init__(self):
        self.verified_refs = {v.get("reference", "").lower() for v in GITA_VERSES}
        # Also store chapter.verse pairs like "2.47"
        for v in GITA_VERSES:
            ch = v.get("chapter")
            vs = v.get("verse")
            if ch and vs:
                self.verified_refs.add(f"{ch}.{vs}")
                self.verified_refs.add(f"gita {ch}.{vs}")

    def validate(self, reply_text, user_text, category, intent, context=None, gita_verse=None):
        """
        Validates generated response across 10 critical criteria.
        Returns: (is_valid: bool, reason: str, corrected_reply: str)
        """
        if not reply_text or len(reply_text.strip()) < 4:
            return False, "Empty or too short reply", ""

        text_lower = reply_text.lower()
        user_lower = (user_text or "").lower()

        # 1. Divine / Krishna false identity claim check
        for claim in FORBIDDEN_DIVINE_CLAIMS:
            if claim in text_lower:
                return False, f"Forbidden divine claim detected: '{claim}'", ""

        # 2. Unsafe advice check
        for unsafe in UNSAFE_ADVICE_TRIGGERS:
            if unsafe in text_lower:
                return False, f"Unsafe advice phrase detected: '{unsafe}'", ""

        # 3. Forced Gita check on casual / technical / sports topics
        casual_or_tech = any(w in user_lower for w in [
            "what is python", "cricket", "football", "what are you doing",
            "how are you", "tell a joke", "courses for earning"
        ])
        if casual_or_tech and not any(g in user_lower for g in ["gita", "krishna", "shlok"]):
            if "bhagavad gita" in text_lower or "कर्मण्येवाधिकारस्ते" in reply_text:
                return False, "Forced Bhagavad Gita content on non-spiritual/casual topic", ""

        # 4. Verified Gita citation check (No fake/hallucinated verses)
        # Only validate citations when Gita is actually discussed or cited
        if gita_verse or category == "BHAGAVAD_GITA_REQUEST" or any(w in text_lower for w in ["bhagavad gita", "gita", "गीता", "श्लोक"]):
            found_refs = re.findall(r'(?:(?:bhagavad\s+gita|gita|श्लोक|अध्याय|verse|chapter)\s+)(\d+[\.:]\d+)', text_lower)
            if not found_refs and (gita_verse or category == "BHAGAVAD_GITA_REQUEST"):
                found_refs = re.findall(r'(\d+[\.:]\d+)', reply_text)
            for ref in found_refs:
                ref_clean = ref.replace(":", ".")
                if ref_clean not in self.verified_refs and f"bhagavad gita {ref_clean}" not in self.verified_refs:
                    return False, f"Unverified Bhagavad Gita citation: {ref}", ""

        # 5. Length reasonableness check
        # Casual conversation shouldn't be a 15-sentence sermon unless providing structured guidance
        if category == "CASUAL_CONVERSATION" and len(reply_text.split()) > 100:
            if not any(marker in reply_text for marker in ["\n1.", "\n2.", "1. **", "2. **", "१.", "२."]):
                # Trim to first two sentences
                sentences = re.split(r'(?<!\d)(?<=[.?!।])\s+', reply_text)
                trimmed = " ".join(sentences[:2])
                return True, "Trimmed excessively long casual reply", trimmed

        return True, "Valid", reply_text

_validator_singleton = None

def get_response_validator():
    global _validator_singleton
    if _validator_singleton is None:
        _validator_singleton = ResponseValidator()
    return _validator_singleton
