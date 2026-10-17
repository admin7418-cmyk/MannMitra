import re
from utils.text_utils import clean_for_matching
from services.gita_service import should_include_gita, recommend, is_problem_requiring_guidance
from services.retrieval_service import get_retrieval_service
from services.repetition_service import get_repetition_service
from services.llm_service import LocalLLM
from services.conversation_manager import get_conversation_manager

RESPONSE_POOLS = {
    "anxiety": [
        {
            "id": "anx_1",
            "en": "I hear you, my friend. Feeling overwhelmed usually happens when our minds try to carry everything all at once. Take a slow, deep breath with me. What is the single heaviest thought on your mind right now?",
            "hi": "मैं आपकी बात समझ रहा हूँ मेरे दोस्त। जब हम एक साथ सब कुछ ठीक करने की कोशिश करते हैं, तो घबराहट होना स्वाभाविक है। एक गहरी साँस लें। इस समय कौन सा विचार आपके मन पर सबसे भारी लग रहा है?",
            "hinglish": "Main samajh sakta hoon mere dost. Jab mind ek saath saari cheezon ko solve karne ki koshish karta hai, toh anxiety badh jati hai. Ek gehri saans lo. Abhi is waqt sabse zyada tension kis baat ki hai?"
        },
        {
            "id": "anx_2",
            "en": "It sounds like you have been carrying quite a lot today. You don't have to sort out the entire future this very second. What part of today has felt the most demanding?",
            "hi": "ऐसा लगता है कि आज आप काफी बोझ महसूस कर रहे हैं। आपको इसी क्षण पूरे भविष्य की चिंता करने की ज़रूरत नहीं है। आज का कौन सा हिस्सा आपके लिए सबसे कठिन रहा?",
            "hinglish": "Lagta hai aaj ka din kaafi exhausting raha hai. Abhi is pal mein puri life figure out karne ki tension mat lo. Aaj sabse mushkil kya laga?"
        },
        {
            "id": "anx_3",
            "en": "When anxiety peaks, our thoughts tend to run way ahead of reality. Remember that you are safe in this present moment. Would you like to tell me what triggered this feeling?",
            "hi": "जब चिंता बढ़ती है, तो हमारे विचार वास्तविकता से बहुत आगे भागने लगते हैं। याद रखें कि इस वर्तमान क्षण में आप सुरक्षित हैं। क्या आप बताना चाहेंगे कि किस बात से यह बेचैनी शुरू हुई?",
            "hinglish": "Jab anxiety peak pe hoti hai, dimag worst-case scenarios sochne lagta hai. Par yaad rakho, tum abhi safe ho. Aisa kya hua jisne ye overthinking start ki?"
        },
        {
            "id": "anx_4",
            "en": "Sometimes putting a feeling into words makes it a little easier to understand. What's troubling you right now?",
            "hi": "कभी-कभी अपनी भावना को शब्दों में बयां करने से मन थोड़ा हल्का हो जाता है। अभी आपको सबसे ज्यादा क्या सता रहा है?",
            "hinglish": "Kabhi-kabhi bol dene se mann halka ho jata hai. Abhi sabse zyada kya pareshan kar raha hai?"
        },
        {
            "id": "anx_5",
            "en": "Take your time, my friend. Feeling overwhelmed is your mind's signal that it needs a brief pause. Let's unpack this together, one gentle step at a time. What would bring you a bit of relief right now?",
            "hi": "जल्दबाजी मत कीजिए। बेचैनी आपके मन का यह संकेत है कि उसे थोड़े विश्राम की आवश्यकता है। हम धीरे-धीरे इसे समझ सकते हैं। इस समय क्या करने से आपको थोड़ी राहत मिल सकती है?",
            "hinglish": "Aaram se dost, koi jaldi nahi. Overwhelmed feel hona batata hai ki mind ko thoda break chahiye. Hum milkar isko handle karenge. Abhi thoda sukoon kis cheez se mil sakta hai?"
        },
        {
            "id": "anx_6",
            "en": "That sounds difficult. What has been weighing on you the most?",
            "hi": "यह समय सचमुच कठिन लग रहा है। कौन सा बोझ आपके दिल पर सबसे ज्यादा भारी पड़ रहा है?",
            "hinglish": "Ye sach mein tough lag raha hai. Kaun si baat sabse zyada dukh de rahi hai?"
        },
        {
            "id": "anx_7",
            "en": "You don't have to explain everything at once. What part of this feels hardest?",
            "hi": "आपको सब कुछ एक साथ समझाने की जरूरत नहीं है। इस समय सबसे कठिन क्या लग रहा है?",
            "hinglish": "Sab kuch ek saath explain karne ki zaroorat nahi hai dost. Is situation ka sabse mushkil hissa kya lag raha hai?"
        },
        {
            "id": "anx_8",
            "en": "It seems like you've been carrying quite a lot. Would you like to tell me what happened?",
            "hi": "ऐसा लगता है कि आप काफी समय से बहुत कुछ अकेले सह रहे हैं। क्या आप बताना चाहेंगे कि क्या हुआ था?",
            "hinglish": "Aisa lag raha hai tum kaafi time se bohot kuch akele jhel rahe ho. Kya share karna chahoge kya baat hui?"
        }
    ],
    "sadness": [
        {
            "id": "sad_1",
            "en": "That sounds difficult. What has been weighing on you the most?",
            "hi": "यह समय कठिन लग रहा है मेरे दोस्त। कौन सी बात आपके मन पर सबसे भारी पड़ रही है?",
            "hinglish": "Ye waqt kaafi tough lag raha hai dost. Kaun si baat sabse zyada bojh bani hui hai?"
        },
        {
            "id": "sad_2",
            "en": "It seems like you've been carrying quite a lot. Would you like to tell me what happened?",
            "hi": "ऐसा लगता है कि आप बहुत कुछ अकेले संभाल रहे हैं। अगर आप सहज महसूस करें, तो क्या आप बताएंगे क्या हुआ?",
            "hinglish": "Aisa lagta hai bohot dino se bojh sambhal rahe ho. Agar batana chaho toh batao kya hua?"
        },
        {
            "id": "sad_3",
            "en": "Sometimes putting a feeling into words makes it a little easier to understand. What's troubling you right now?",
            "hi": "कभी-कभी अपनी तकलीफ को शब्दों में कहना उसे थोड़ा आसान बना देता है। अभी आपको सबसे ज्यादा क्या परेशान कर रहा है?",
            "hinglish": "Kabhi-kabhi feeling ko words mein express karne se mann halka hota hai. Abhi kya pareshan kar raha hai?"
        },
        {
            "id": "sad_4",
            "en": "You don't have to explain everything at once. What part of this feels hardest?",
            "hi": "आपको सब कुछ एक साथ बताने की कोई मजबूरी नहीं है। इस बात का कौन सा हिस्सा सबसे दर्दनाक लग रहा है?",
            "hinglish": "Ek hi baar mein sab kuch batane ki tension mat lo. Sabse zyada dard kis baat ka ho raha hai?"
        },
        {
            "id": "sad_5",
            "en": "I am right here with you. It is okay to feel sad and not have everything figured out today. What thought keeps repeating in your head?",
            "hi": "मैं पूरी तरह आपके साथ हूँ। उदास महसूस करना स्वाभाविक है। कौन सा विचार आपके मन में बार-बार आ रहा है?",
            "hinglish": "Main tumhare saath hoon dost. Udas hona natural hai. Kaun sa thought baar-baar dimag mein ghoom raha hai?"
        }
    ],
    "loneliness": [
        {
            "id": "lon_1",
            "en": "Feeling lonely can make everything feel quiet and heavy. But you are not alone here; I am genuinely glad to chat with you. What has been making you feel isolated?",
            "hi": "अकेलापन महसूस होना मन को बहुत भारी कर देता है। लेकिन आप यहाँ अकेले नहीं हैं; मैं आपके साथ बात करने के लिए हमेशा उपलब्ध हूँ। क्या बात आपको अकेला महसूस करा रही है?",
            "hinglish": "Akelapan dil ko bhari kar deta hai dost. Par tum yahan akele nahi ho, main sun raha hoon. Kya baat tumhe akela feel kara rahi hai?"
        },
        {
            "id": "lon_2",
            "en": "It seems like you've been carrying quite a lot alone lately. Would you like to tell me what happened?",
            "hi": "ऐसा लगता है कि आप काफी समय से बहुत कुछ अकेले संभाल रहे हैं। अगर आप बताना चाहें, तो क्या हुआ?",
            "hinglish": "Aisa lagta hai bohot dino se bojh sambhal rahe ho. Agar share karna chaho toh batao kya hua?"
        }
    ]
}

class ResponseManager:
    def __init__(self):
        self.retrieval_service = get_retrieval_service()
        self.repetition_service = get_repetition_service()
        self.conversation_manager = get_conversation_manager()

    def generate_response(self, user_text, category, intent, topic, mood, context, lang="en"):
        """
        Deterministic decision controller enforcing user priority rules:
        1. Safety (handled prior)
        2. Understand user intent
        3. Answer actual question
        4. Use conversation context
        5. Give practical help
        6. Use Gita only when relevant
        7. Keep response natural and concise
        """
        context = context or {}
        turn_count = context.get("turn_count", 0)
        recent_messages = context.get("recent_messages", [])
        recent_bot_texts = [
            m.get("text", "") for m in recent_messages if m.get("role") == "assistant"
        ][-4:]

        gita_data = None
        reply_text = ""
        res_type = intent

        # Branch 1: Explicit Bhagavad Gita Request or Shloka Inquiry
        if category == "BHAGAVAD_GITA_REQUEST" or should_include_gita(intent, user_text, context):
            gita_data, score = self.retrieval_service.retrieve(user_text, intent=intent, lang=lang, force=True)
            if not gita_data:
                gita_data = recommend(user_text, lang=lang)
            res_type = "gita"

            reply_text = LocalLLM.generate(
                prompt=user_text,
                context=context,
                category=category,
                intent=intent,
                user_text=user_text,
                gita_verse=gita_data,
                lang=lang,
                turn_count=turn_count
            )
            # Ensure complete answer with shloka & solution even if LLM returned empty or generic fallback
            generic_phrases = ["main sun raha", "listening closely", "aap bejhijhak", "thoda aur batao", "मैं आपकी बात ध्यान"]
            if not reply_text or len(reply_text.strip()) < 35 or any(gp in reply_text.lower() for gp in generic_phrases):
                reply_text = self._format_gita_response(gita_data, user_text, lang)
            elif gita_data:
                # If reply_text does not contain practical solutions/steps, append them so the user is never left without solutions
                has_solutions = any(sol in reply_text for sol in ["1.", "१.", "Step 1", "कदम", "समाधान", "Solution", "व्यावहारिक"])
                if not has_solutions:
                    guidance = gita_data.get("active_guidance") or gita_data.get("practical_interpretation", "")
                    if guidance:
                        if lang == "hi":
                            reply_text += (
                                f"\n\n**व्यावहारिक मार्गदर्शन और समाधान:**\n"
                                f"१. परिणाम और भविष्य के भय को छोड़कर वर्तमान कार्य पर ध्यान दें।\n"
                                f"२. {guidance}\n"
                                f"३. आज ही बिना तनाव लिए एक छोटा कदम आगे बढ़ाएं।"
                            )
                        elif lang == "hinglish":
                            reply_text += (
                                f"\n\n**Practical Solutions & Next Steps:**\n"
                                f"1. Future results ki overthinking chhod kar present task aur effort par focus karo.\n"
                                f"2. {guidance}\n"
                                f"3. Sab kuch ek sath solve karne ke bajay abhi sirf ek small focused step lo."
                            )
                        else:
                            reply_text += (
                                f"\n\n**Practical Solutions & Next Steps:**\n"
                                f"1. Release anxious fixation on future results and anchor your attention in immediate effort.\n"
                                f"2. {guidance}\n"
                                f"3. Break the overwhelming situation into one tiny manageable action right now."
                            )

        # Branch 2: General Question (Technical, Sports, Informational) -> NO GITA
        elif category == "GENERAL_QUESTION":
            res_type = "informational"
            reply_text = LocalLLM.generate(
                prompt=user_text,
                context=context,
                category=category,
                intent=intent,
                user_text=user_text,
                gita_verse=None,
                lang=lang,
                turn_count=turn_count
            )

        # Branch 3: Advice or Decision (Career, Sports, Earning, Courses, Ambition) -> Practical Guidance
        elif category == "ADVICE_OR_DECISION":
            res_type = "advice"
            if intent == "life_ambition_big":
                if lang == "hi":
                    reply_text = "जीवन में कुछ बड़ा और सार्थक करने की महत्वाकांक्षा (ambition) ही हर महान उपलब्धि की शुरुआत होती है। अपने इस लक्ष्य को हकीकत में बदलने के लिए, किसी एक महत्वपूर्ण कौशल को गहराई से सीखें, प्रतिदिन स्वाध्याय करें और रोज़ एक छोटा कदम उठाएं।"
                elif lang == "hinglish":
                    reply_text = "Zindagi mein kuch bada karne ka ambition hona hi sabse pehla step hota hai! Apne is ambition ko reality banane ke liye roz ek valuable skill master karo aur consistent disciplined steps lo."
                else:
                    reply_text = (
                        "Having big ambition is the first step toward purpose. "
                        "To turn high ambition into reality, focus on mastering one valuable skill deeply, "
                        "reading daily, and executing small consistent steps every single day."
                    )
            else:
                reply_text = LocalLLM.generate(
                    prompt=user_text,
                    context=context,
                    category=category,
                    intent=intent,
                    user_text=user_text,
                    gita_verse=None,
                    lang=lang,
                    turn_count=turn_count
                )

        # Branch 4: Personal Sharing (Reflecting, Day's Effort, Thoughts) -> Active Listening
        elif category == "PERSONAL_SHARING":
            res_type = "personal_sharing"
            reply_text = LocalLLM.generate(
                prompt=user_text,
                context=context,
                category=category,
                intent=intent,
                user_text=user_text,
                gita_verse=None,
                lang=lang,
                turn_count=turn_count
            )

        # Branch 5: Emotional Support (Struggle, Exam Anxiety, Sadness, Failure)
        elif category == "EMOTIONAL_SUPPORT":
            user_lower = (user_text or "").lower()
            is_continuation = user_lower.strip().rstrip(".?!") in ["my exams", "my exam", "the result", "result"]
            is_failure = any(w in user_lower for w in ["i failed my exam", "failed my test", "i flunked", "fail ho gaya", "i still failed"])
            is_future_fear = any(w in user_lower for w in ["scared about my future", "scared of future", "fear of future", "scared about future"])

            # Situations where Gita is genuinely relevant:
            # 1. Explicit request for Gita / Krishna
            # 2. Exam stress / anxiety statements (e.g. "I feel so stressed about my exams", "परीक्षा को लेकर बहुत चिंता")
            # 3. Seeking practical solutions for overthinking / stress ("overthinking ho rahi hai kya karu")
            is_exam_stress = any(w in user_lower for w in ["stressed about my exams", "exam tension", "anxious about my exams", "exam stress", "परीक्षा को लेकर", "परीक्षा की चिंता"])
            is_guidance_request = any(w in user_lower for w in ["what should i do", "what to do", "solution", "kya karu", "kaise karu", "suggest", "guide me", "help me"])
            is_overthink_guidance = is_guidance_request and any(w in user_lower for w in ["overthink", "overthinking", "stress", "tension", "dimag", "soch"])
            is_problem = is_problem_requiring_guidance(user_text, intent, category)
            is_pure_venting = (
                (intent in ["sadness", "loneliness"] or any(w in user_lower for w in ["feel so sad", "feel sad", "feeling sad", "feel lonely", "feel so lonely", "feeling lonely", "very sad", "very lonely", "bahut akela", "bahut udas"]))
                and not is_guidance_request
            )
            recent_user_texts = [m["text"] for m in context.get("recent_messages", []) if m.get("role") == "user"]
            is_repeating_same_message = (len(recent_user_texts) >= 1 and clean_for_matching(user_text) == clean_for_matching(recent_user_texts[-1]))

            should_use_gita = (
                not is_continuation and not is_failure and not is_future_fear and not is_pure_venting and not is_repeating_same_message and (
                    should_include_gita(intent, user_text, context) or
                    is_exam_stress or
                    is_overthink_guidance or
                    is_problem
                )
            )

            if should_use_gita:
                gita_data, score = self.retrieval_service.retrieve(user_text, intent=intent, lang=lang, threshold=0.25)
                if not gita_data:
                    gita_data = recommend(user_text, lang=lang)

            if gita_data:
                res_type = "gita"
                reply_text = self._format_gita_response(gita_data, user_text, lang)
            else:
                res_type = "emotional_support"
                # Check if LocalLLM has a specific intent generator (e.g. failure, scared about future)
                smart_rep = LocalLLM.generate(
                    prompt=user_text,
                    context=context,
                    category=category,
                    intent=intent,
                    user_text=user_text,
                    gita_verse=None,
                    lang=lang,
                    turn_count=turn_count
                )
                fallback_triggers = [
                    "i am listening closely", "main sun raha hoon", "मैं आपकी बात ध्यान से सुन रहा"
                ]
                if smart_rep and not any(fb in smart_rep.lower() for fb in fallback_triggers):
                    reply_text = smart_rep
                else:
                    # Select from response pool avoiding recently used response IDs
                    pool_family = "sadness" if (intent in ["sadness", "loneliness"] or any(w in user_lower for w in ["sad", "lonely", "akela", "udas"])) else "anxiety"
                    reply_text, chosen_id = self._select_from_pool(pool_family, lang, context)

        # Branch 5B: Special intent guarantees
        elif intent == "friendship":
            res_type = "friendship"
            if lang == "hi":
                reply_text = "हाँ, बिल्कुल! मुझे आपका मित्र बनकर बहुत खुशी होगी। एक सच्चा दोस्त होने के नाते, मैं हमेशा आपके साथ रहूँगा और आपकी बात सुनूँगा।"
            elif lang == "hinglish":
                reply_text = "Haan bilkul! Mujhe tumhara dost ban kar bohot khushi hogi. Ek saccha friend hone ke nate main hamesha tumhare sath hoon."
            else:
                reply_text = "Yes, absolutely! I would love to be your friend. True friendship is built on mutual trust, listening without judgment, and walking together through life. I am right here with you."

        # Branch 6: Casual Conversation & General Knowledge (Powered by Ollama)
        else:
            res_type = "casual"
            reply_text = LocalLLM.generate(
                prompt=user_text,
                context=context,
                category=category,
                intent=intent,
                user_text=user_text,
                gita_verse=None,
                lang=lang,
                turn_count=turn_count
            )

        # Clean any redundant self-introductions if not turn 1
        reply_text = self.repetition_service.clean_redundant_intros(reply_text, turn_count)

        # Check similarity against recent bot responses to prevent repetition
        if gita_data is None and intent != "friendship":
            is_repetitive, sim_score, matched = self.repetition_service.is_too_similar(reply_text, recent_bot_texts)
            if is_repetitive and matched:
                if category == "EMOTIONAL_SUPPORT":
                    pool_family = "sadness" if (intent in ["sadness", "loneliness"] or any(w in user_lower for w in ["sad", "lonely", "akela", "udas"])) else "anxiety"
                    reply_text, _ = self._select_from_pool(pool_family, lang, context)
                elif category in ["ADVICE_OR_DECISION", "GENERAL_QUESTION"]:
                    if clean_for_matching(reply_text) == clean_for_matching(matched):
                        if lang == "hi":
                            reply_text = "इसके साथ ही, सबसे महत्वपूर्ण यह है कि आप आज से ही एक छोटा कदम शुरू करें। आप किस विकल्प से शुरुआत करना चाहेंगे?"
                        elif lang == "hinglish":
                            reply_text = "Iske sath hi dost, sabse zaroori ye hai ki pehla chhota action lo. Tum kis step se shuru karna chahte ho?"
                        else:
                            reply_text = "Building directly on that, the most practical approach is taking one focused first step today. Which option feels most natural to start with?"

        return {
            "reply": reply_text,
            "gita": gita_data,
            "category": category,
            "intent": intent,
            "topic": topic,
            "mood": mood,
            "type": res_type
        }

    def _select_from_pool(self, intent_family, lang, context):
        """
        Priority 3: Selects an unused response pattern from the pool.
        Tracks response IDs and rotates intelligently when exhausted.
        """
        pool = RESPONSE_POOLS.get(intent_family) or RESPONSE_POOLS["anxiety"]
        used_ids = set(context.get("recent_response_ids", []))

        # 1. Prefer unused response patterns
        available = [p for p in pool if p["id"] not in used_ids]

        # 2. Reset / rotate intelligently when pool is exhausted
        if not available:
            pool_ids = {p["id"] for p in pool}
            context["recent_response_ids"] = [
                rid for rid in context.get("recent_response_ids", []) if rid not in pool_ids
            ]
            available = pool

        # Deterministic rotation based on turn_count to avoid random repetition
        turn = context.get("turn_count", 0)
        idx = turn % len(available)
        chosen = available[idx]

        # Track response ID
        chosen_id = chosen["id"]
        context.setdefault("recent_response_ids", []).append(chosen_id)
        if len(context["recent_response_ids"]) > 30:
            context["recent_response_ids"] = context["recent_response_ids"][-30:]

        text = chosen.get(lang) or chosen.get("en")
        return text, chosen_id

    def _format_gita_response(self, gita_data, user_text, lang):
        if not gita_data:
            return ""
        ref = gita_data.get("reference", "Bhagavad Gita")
        sanskrit = gita_data.get("sanskrit", "")
        meaning = gita_data.get("active_meaning") or gita_data.get("simple_meaning", "")
        guidance = gita_data.get("active_guidance") or gita_data.get("practical_interpretation", "")

        if lang == "hi":
            return (
                f"मैं आपकी मनःस्थिति को पूरी तरह समझ सकता हूँ मेरे मित्र। जब तनाव या चिंता बढ़ती है, तो मन अशांत हो जाता है:\n\n"
                f"📜 **श्रीमद्भगवद्गीता ({ref})**\n\"{sanskrit}\"\n\n"
                f"**श्लोक का सरल और स्पष्ट अर्थ:**\n{meaning}\n\n"
                f"**व्यावहारिक मार्गदर्शन और समाधान:**\n"
                f"१. परिणाम और भविष्य के भय को छोड़कर वर्तमान कार्य और प्रयास पर एकाग्र हों।\n"
                f"२. {guidance}\n"
                f"३. अपने मन को एक सच्चा मित्र बनाएं और घबराने के बजाय आज ही एक छोटा कदम उठाएं।"
            )
        elif lang == "hinglish":
            return (
                f"Main samajh sakta hoon mere dost, jab stress ya fear of failure aata hai toh mind heavy ho jata hai. Bhagavad Gita humein sahi direction deti hai:\n\n"
                f"📜 **Shrimad Bhagavad Gita ({ref})**\n\"{sanskrit}\"\n\n"
                f"**Gita Shlok ka Simple Meaning:**\n{meaning}\n\n"
                f"**Practical Solutions & Next Steps:**\n"
                f"1. Result ya future ki overthinking chhod kar present task aur effort par focus karo.\n"
                f"2. {guidance}\n"
                f"3. Sab kuch ek sath solve karne ke bajay abhi sirf ek small focused step lo."
            )
        else:
            return (
                f"I hear how heavy things feel right now, my friend. When stress or fear of failure mounts, the Bhagavad Gita offers timeless wisdom and steady guidance:\n\n"
                f"📜 **Shrimad Bhagavad Gita ({ref})**\n\"{sanskrit}\"\n\n"
                f"**Simple Meaning of the Shloka:**\n{meaning}\n\n"
                f"**Practical Solutions & Next Steps:**\n"
                f"1. Release anxious fixation on future results and anchor your attention in immediate effort.\n"
                f"2. {guidance}\n"
                f"3. Break the overwhelming situation into one tiny manageable action right now."
            )

_resp_manager_singleton = None

def get_response_manager():
    global _resp_manager_singleton
    if _resp_manager_singleton is None:
        _resp_manager_singleton = ResponseManager()
    return _resp_manager_singleton
