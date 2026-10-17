import json
import re
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
from database.connection import get_db, DB_FILE, check_mongo_available, get_mongo_db

_IN_MEMORY_PROFILES: Dict[str, Dict[str, Any]] = {}

class MemoryLearningService:
    """
    Local Long-Term Learning and Adaptive Memory Engine for Madhav.
    Learns user goals, interests, concerns, and feedback completely offline.
    Zero cloud APIs. 100% private to the user's local database.
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        """Loads persistent user memory from database or memory cache."""
        uid = str(user_id or "anonymous_user")
        if uid in self._cache:
            return self._cache[uid]

        memory = self._load_from_db(uid)
        if not memory:
            memory = {
                "user_id": uid,
                "name": "",
                "career_interest": "",
                "primary_goal": "",
                "known_concerns": [],
                "preferences": {"preferred_tone": "practical", "fav_topics": []},
                "last_discussed_topic": "",
                "interaction_count": 0,
                "positive_feedback_count": 0,
                "negative_feedback_count": 0,
                "updated_at": datetime.now().isoformat()
            }
        self._cache[uid] = memory
        return memory

    def _load_from_db(self, user_id: str) -> Optional[Dict[str, Any]]:
        uid = str(user_id)
        if check_mongo_available():
            try:
                db = get_mongo_db()
                doc = db.user_memory.find_one({"user_id": uid})
                if doc:
                    doc.pop("_id", None)
                    return doc
            except Exception:
                pass

        # SQLite
        try:
            con = sqlite3.connect(DB_FILE)
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM user_memory WHERE user_id = ?", (uid,))
            row = cur.fetchone()
            con.close()
            if row:
                return {
                    "user_id": row["user_id"],
                    "name": row["name"] or "",
                    "career_interest": row["career_interest"] or "",
                    "primary_goal": row["primary_goal"] or "",
                    "known_concerns": json.loads(row["known_concerns"] or "[]"),
                    "preferences": json.loads(row["preferences"] or "{}"),
                    "last_discussed_topic": row["last_discussed_topic"] or "",
                    "interaction_count": int(row["interaction_count"] or 0),
                    "positive_feedback_count": int(row["positive_feedback_count"] or 0),
                    "negative_feedback_count": int(row["negative_feedback_count"] or 0),
                    "updated_at": row["updated_at"] or datetime.now().isoformat()
                }
        except Exception:
            pass

        return _IN_MEMORY_PROFILES.get(uid)

    def save_user_memory(self, memory: Dict[str, Any]) -> None:
        """Persists user memory to database and updates cache."""
        uid = str(memory["user_id"])
        memory["updated_at"] = datetime.now().isoformat()
        self._cache[uid] = memory
        _IN_MEMORY_PROFILES[uid] = memory

        if check_mongo_available():
            try:
                db = get_mongo_db()
                db.user_memory.update_one(
                    {"user_id": uid},
                    {"$set": memory},
                    upsert=True
                )
                return
            except Exception:
                pass

        try:
            con = sqlite3.connect(DB_FILE)
            cur = con.cursor()
            cur.execute("""
                INSERT INTO user_memory (
                    user_id, name, career_interest, primary_goal, known_concerns,
                    preferences, last_discussed_topic, interaction_count,
                    positive_feedback_count, negative_feedback_count, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = excluded.name,
                    career_interest = excluded.career_interest,
                    primary_goal = excluded.primary_goal,
                    known_concerns = excluded.known_concerns,
                    preferences = excluded.preferences,
                    last_discussed_topic = excluded.last_discussed_topic,
                    interaction_count = excluded.interaction_count,
                    positive_feedback_count = excluded.positive_feedback_count,
                    negative_feedback_count = excluded.negative_feedback_count,
                    updated_at = excluded.updated_at
            """, (
                uid,
                memory.get("name", ""),
                memory.get("career_interest", ""),
                memory.get("primary_goal", ""),
                json.dumps(memory.get("known_concerns", [])),
                json.dumps(memory.get("preferences", {})),
                memory.get("last_discussed_topic", ""),
                memory.get("interaction_count", 0),
                memory.get("positive_feedback_count", 0),
                memory.get("negative_feedback_count", 0),
                memory["updated_at"]
            ))
            con.commit()
            con.close()
        except Exception:
            pass

    def extract_and_update_learnings(self, user_id: str, user_text: str, bot_reply: str,
                                     intent: str = "", category: str = "", topic: str = "") -> Dict[str, Any]:
        """
        Dynamically discovers and updates user facts from conversation.
        Runs safely in pure local Python with zero external API calls.
        """
        memory = self.get_user_memory(user_id)
        memory["interaction_count"] += 1
        if topic:
            memory["last_discussed_topic"] = topic

        lower = (user_text or "").lower()

        # 1. Name learning
        name_match = re.search(r'\b(?:my name is|mera naam|call me|i am|naam hai)\s+([a-zA-Z\u0900-\u097f]+)\b', user_text, re.IGNORECASE)
        if name_match:
            cand = name_match.group(1).strip()
            if cand.lower() not in ["madhav", "krishna", "user", "fine", "good", "sad", "stressed", "feeling"]:
                memory["name"] = cand.capitalize()

        # 2. Career & skill interest learning
        career_keywords = {
            "python": "Python programming",
            "web development": "Web Development",
            "freelancing": "Freelancing",
            "coding": "Software Engineering & Coding",
            "data science": "Data Science & AI",
            "machine learning": "Machine Learning",
            "sarkari naukri": "Government exams preparation",
            "सरकारी नौकरी": "सरकारी नौकरी तैयारी",
            "upsc": "Civil Services / UPSC",
            "cricket": "Cricket & Sports",
            "fitness": "Fitness & Training",
            "ui/ux": "UI/UX Design",
            "digital marketing": "Digital Marketing"
        }
        for kw, desc in career_keywords.items():
            if kw in lower:
                if not memory["career_interest"] or kw in lower:
                    memory["career_interest"] = desc
                favs = memory["preferences"].setdefault("fav_topics", [])
                if desc not in favs:
                    favs.append(desc)
                    if len(favs) > 5:
                        favs.pop(0)
                break

        # 3. Primary goal learning
        if any(w in lower for w in ["for freelancing", "freelancing karna", "freelance"]):
            memory["primary_goal"] = "Freelancing"
        elif any(w in lower for w in ["for a job", "placement", "job chahiye", "naukri"]):
            memory["primary_goal"] = "Full-time Job / Placement"
        elif any(w in lower for w in ["earning", "earn money", "kamana"]):
            memory["primary_goal"] = "Skill-based Earning"
        elif any(w in lower for w in ["exam pass", "clear exam", "exam crack", "marks"]):
            memory["primary_goal"] = "Academic / Exam Success"

        # 4. Known concern / psychological triggers learning
        concerns = set(memory.get("known_concerns", []))
        if any(w in lower for w in ["procrastinat", "aalsi", "time waste", "can't focus", "dhyan nahi"]):
            concerns.add("Procrastination & Focus")
        if any(w in lower for w in ["neend nahi", "can't sleep", "overthinking at night", "insomnia"]):
            concerns.add("Nighttime Overthinking & Sleep")
        if any(w in lower for w in ["exam tension", "exam stress", "marks ki tension", "syllabus"]):
            concerns.add("Exam Anxiety")
        if any(w in lower for w in ["failed", "fail ho gaya", "flunked"]):
            concerns.add("Overcoming Failure")
        if any(w in lower for w in ["friend stopped talking", "jhagda ho gaya", "fight with friend"]):
            concerns.add("Friend / Social Conflict")
        if any(w in lower for w in ["low confidence", "imposter syndrome", "not good enough"]):
            concerns.add("Self-Confidence")

        memory["known_concerns"] = list(concerns)[:6]

        # 5. Tone preference adaptation
        if category == "ADVICE_OR_DECISION":
            memory["preferences"]["preferred_tone"] = "actionable_roadmaps"
        elif category == "EMOTIONAL_SUPPORT":
            memory["preferences"]["preferred_tone"] = "compassionate_grounding"

        self.save_user_memory(memory)
        return memory

    def record_feedback(self, user_id: str, response_id: str = "", rating: int = 1,
                        comment: str = "", category: str = "", intent: str = "", theme_id: str = "") -> Dict[str, Any]:
        """
        Records user feedback (RLUF - Reinforcement Learning from User Feedback).
        rating: +1 (helpful / 👍) or -1 (unhelpful / 👎)
        """
        uid = str(user_id or "anonymous_user")
        now = datetime.now().isoformat()

        # Update user profile counts
        memory = self.get_user_memory(uid)
        if rating > 0:
            memory["positive_feedback_count"] = memory.get("positive_feedback_count", 0) + 1
        else:
            memory["negative_feedback_count"] = memory.get("negative_feedback_count", 0) + 1
        self.save_user_memory(memory)

        # Record to SQLite database
        try:
            con = sqlite3.connect(DB_FILE)
            cur = con.cursor()
            cur.execute("""
                INSERT INTO response_feedback (
                    user_id, response_id, category, intent, theme_id, rating, comment, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (uid, response_id, category, intent, theme_id, rating, comment, now))
            con.commit()
            con.close()
        except Exception:
            pass

        return {
            "status": "success",
            "user_id": uid,
            "rating": rating,
            "positive_total": memory["positive_feedback_count"],
            "negative_total": memory["negative_feedback_count"]
        }

    def get_personalized_greeting(self, user_id: str, lang: str = "en") -> Optional[str]:
        """
        Creates a warm greeting for returning users referencing learned memory.
        """
        memory = self.get_user_memory(user_id)
        if memory.get("interaction_count", 0) < 2:
            return None

        name = memory.get("name", "")
        name_prefix = f", {name}" if name else ""
        name_hi = f" {name}" if name else ""
        interest = memory.get("career_interest") or memory.get("primary_goal")

        if lang == "hi":
            if interest:
                return f"नमस्ते{name_hi}! आपको दोबारा देखकर बहुत अच्छा लगा। आपकी {interest} से जुड़ी तैयारी या दिन कैसा चल रहा है?"
            return f"नमस्ते{name_hi}! मनमित्र में आपका पुनः स्वागत है। आज आपका दिन कैसा बीत रहा है?"
        elif lang == "hinglish":
            if interest:
                return f"Welcome back dost{name_prefix}! Wapas connect hokar accha laga. Tumhari {interest} ki progress kaisi chal rahi hai?"
            return f"Welcome back dost{name_prefix}! Wapas connect hokar khushi hui. Aaj kaisa chal raha hai sab?"
        else:
            if interest:
                return f"Welcome back, my friend{name_prefix}! It's great to connect again. How has your progress been with {interest}?"
            return f"Hello again, my friend{name_prefix}! Welcome back. How is your day treating you today?"

    def clear_user_memory(self, user_id: str) -> None:
        """Completely clears all learned data for a user for privacy."""
        uid = str(user_id or "anonymous_user")
        self._cache.pop(uid, None)
        _IN_MEMORY_PROFILES.pop(uid, None)

        try:
            con = sqlite3.connect(DB_FILE)
            cur = con.cursor()
            cur.execute("DELETE FROM user_memory WHERE user_id = ?", (uid,))
            cur.execute("DELETE FROM response_feedback WHERE user_id = ?", (uid,))
            con.commit()
            con.close()
        except Exception:
            pass

_learning_service_instance = None

def get_memory_learning_service() -> MemoryLearningService:
    global _learning_service_instance
    if _learning_service_instance is None:
        _learning_service_instance = MemoryLearningService()
    return _learning_service_instance
