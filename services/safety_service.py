import re

CRISIS_INDICATORS = [
    # English
    "i want to die", "kill myself", "end my life", "suicide", "suicidal",
    "hurt myself", "cant take this anymore", "can't take this anymore",
    "better off dead", "give up on life", "no reason to live", "hang myself",
    "cut myself", "slit my", "overdose", "jump off", "end it all", "want to disappear forever",
    "hurt someone", "kill someone",
    # Hindi Devanagari
    "मरना चाहता", "मरना चाहती", "खुद को नुकसान", "आत्महत्या", "जान देना",
    "जीना नहीं चाहता", "जीना नहीं चाहती", "अब नहीं सहा जाता", "जीवन समाप्त",
    "खुद को चोट", "फांसी", "नदी में कूद", "सब खत्म करना चाहता",
    # Hinglish
    "marna chahta", "marna chahti", "marne ka mann", "khud ko khatam",
    "suicide kar", "jaan de dunga", "jaan de dungi", "zindagi khatam",
    "ab aur nahi saha ja raha", "khud ko hurt", "jeena nahi chahta", "sab khatam karne ka mann",
    "zehar khaa", "chhat se kood"
]

SAFETY_RESPONSES = {
    "en": [
        (
            "🙏 **I hear you, and your life and safety are what matter most right now.**\n\n"
            "I am a supportive AI companion, not a mental health professional or emergency service, but please know you do not have to carry this immense weight alone. "
            "Are you in a safe place right now? Please reach out to someone you trust—a parent, sibling, teacher, or friend—immediately.\n\n"
            "📞 **Free 24x7 Confidential Indian Crisis Helplines:**\n"
            "• **Tele-MANAS (Govt of India):** [14416](tel:14416) or [1800-891-4416](tel:18008914416)\n"
            "• **KIRAN Mental Health:** [1800-599-0019](tel:18005990019)\n"
            "• **Vandrevala Foundation:** [+91 9999 666 555](tel:9999666555)\n"
            "• **National Emergency Service:** [112](tel:112)\n\n"
            "Please reach out to one of these services or a loved one right away. There are caring people ready to support you through this."
        ),
        (
            "🙏 **Please stay safe. What you are feeling is serious, and your wellbeing is deeply important.**\n\n"
            "When pain feels unbearable, having a real human voice can help anchor you. Please step away from any dangerous situations and speak to a family member, counselor, or trusted adult right now.\n\n"
            "📞 **Immediate 24x7 Help (India):**\n"
            "• **Tele-MANAS:** [14416](tel:14416) / [1800-891-4416](tel:18008914416)\n"
            "• **Vandrevala Foundation Helpline:** [+91 9999 666 555](tel:9999666555)\n"
            "• **National Emergency Number:** [112](tel:112)\n\n"
            "You are not alone, and there is compassionate, professional help available this very minute."
        )
    ],
    "hi": [
        (
            "🙏 **मनमित्र आपकी बात पूरी गंभीरता से सुन रहा है। आपकी सुरक्षा और आपका जीवन सबसे अधिक महत्वपूर्ण है।**\n\n"
            "मैं एक मित्रवत एआई साथी हूँ, कोई डॉक्टर या आपातकालीन सेवा नहीं। कृपया इस कठिन समय में अकेले न रहें। "
            "क्या आप इस समय किसी सुरक्षित स्थान पर हैं? कृपया तुरंत अपने माता-पिता, किसी विश्वासपात्र मित्र या शिक्षक से संपर्क करें।\n\n"
            "📞 **निःशुल्क 24x7 भारतीय हेल्पलाइन:**\n"
            "• **Tele-MANAS (भारत सरकार):** [14416](tel:14416) या [1800-891-4416](tel:18008914416)\n"
            "• **किरण (KIRAN) हेल्पलाइन:** [1800-599-0019](tel:18005990019)\n"
            "• **वंद्रेवाला फाउंडेशन:** [+91 9999 666 555](tel:9999666555)\n"
            "• **आपातकालीन नंबर:** [112](tel:112)\n\n"
            "मदद हमेशा उपलब्ध है मेरे दोस्त। कृपया तुरंत किसी अपने या हेल्पलाइन से बात करें।"
        ),
        (
            "🙏 **कृपया धैर्य रखें मेरे दोस्त। आपकी ज़िंदगी बहुत कीमती है और यह दर्द स्थायी नहीं है।**\n\n"
            "किसी भी भारी परिस्थिति में खुद को अकेला न छोड़ें। कृपया अपने किसी करीबी को कॉल करें या तुरंत नीचे दी गई हेल्पलाइन पर बात करें:\n\n"
            "📞 **24x7 सहायता केंद्र (भारत):**\n"
            "• **Tele-MANAS:** [14416](tel:14416) / [1800-891-4416](tel:18008914416)\n"
            "• **वंद्रेवाला फाउंडेशन:** [+91 9999 666 555](tel:9999666555)\n"
            "• **आपातकालीन सेवा:** [112](tel:112)\n\n"
            "हम आपके साथ हैं, कृपया तुरंत किसी विशेषज्ञ या परिजन से सहायता लें।"
        )
    ],
    "hinglish": [
        (
            "🙏 **MannMitra aapki baat sun raha hai. Aapki safety aur aapki zindagi sabse pehle hai.**\n\n"
            "Main ek AI companion hoon, doctor ya emergency service nahi. Please is mushkil waqt mein akele mat raho. "
            "Kya aap abhi kisi safe jagah par hain? Apne parents, family, kisi trusted dost ya teacher se abhi baat karo.\n\n"
            "📞 **Free 24x7 Verified Indian Helplines:**\n"
            "• **Tele-MANAS (Govt of India):** [14416](tel:14416) / [1800-891-4416](tel:18008914416)\n"
            "• **KIRAN Helpline:** [1800-599-0019](tel:18005990019)\n"
            "• **Vandrevala Foundation:** [+91 9999 666 555](tel:9999666555)\n"
            "• **National Emergency Service:** [112](tel:112)\n\n"
            "Please inmein se kisi ek number par ya kisi apne ko abhi call karo. Halat kitni bhi mushkil ho, madad hamesha available hai."
        ),
        (
            "🙏 **Please safe raho mere dost. Jo tum feel kar rahe ho wo bohot serious hai, aur tum akele nahi ho.**\n\n"
            "Is heavy feeling ko akele jhelne ki zaroorat nahi hai. Abhi kisi family member ya counselor ko phone lagao:\n\n"
            "📞 **Instant Helplines (India):**\n"
            "• **Tele-MANAS:** [14416](tel:14416) / [1800-891-4416](tel:18008914416)\n"
            "• **Vandrevala Foundation:** [+91 9999 666 555](tel:9999666555)\n"
            "• **Emergency Number:** [112](tel:112)\n\n"
            "Yeh log bina judge kiye help karte hain. Please abhi call karo."
        )
    ]
}

def needs_human_support(text):
    if not text:
        return False
    value = text.lower().strip()
    return any(indicator in value for indicator in CRISIS_INDICATORS)

def response(lang="en", variant_idx=0):
    lang = (lang or "en").lower().strip()
    if lang not in ["en", "hi", "hinglish"]:
        lang = "en"
    options = SAFETY_RESPONSES.get(lang, SAFETY_RESPONSES["en"])
    return options[variant_idx % len(options)]
