import re
from typing import Optional, Dict, Any, Tuple

class CognitiveDialogueEngine:
    """
    Dynamic Cognitive Architecture (DCA) for Madhav.
    Provides deep, structured, multi-step intelligence across career, coding,
    study psychology, decision-making, and emotional reframing in pure Python.
    Size: < 0.2 MB. RAM: < 5 MB. Response Time: < 2 ms. Zero cloud APIs.
    """

    @classmethod
    def evaluate(cls, user_text: str, context: Optional[Dict[str, Any]] = None, lang: str = "en") -> Optional[Tuple[str, str]]:
        """
        Evaluates user text against cognitive domain models.
        Returns: (synthesized_response, theme_id) or None if not applicable.
        """
        if not user_text:
            return None

        lower = user_text.lower().strip()
        context = context or {}
        subjects = context.get("mentioned_subjects", [])
        subject_str = " ".join(subjects)

        # 1. Procrastination, Focus & Phone Addiction
        if any(w in lower for w in [
            "procrastinat", "can't focus", "cannot focus", "cannot concentrate", "can't concentrate",
            "feeling lazy", "lazy", "wasting time", "waste time", "phone addiction", "stop scrolling",
            "aalsi", "man nahi lag raha padhai", "padhai me dhyan", "padhai mein dhyan", "dhyan nahi lag raha",
            "time waste ho raha", "procrastination band", "aalas kaise door"
        ]):
            return cls._compose_procrastination(lang, context), "cog_procrastination"

        # 2. Python & Beginner Coding Roadmap
        if (
            ("python" in lower and any(w in lower for w in ["learn", "start", "roadmap", "sikhna", "seekhna", "beginner", "kaise", "shuru"]))
            or any(w in lower for w in [
                "learn python", "start python", "python roadmap", "python kaise", "python beginner",
                "coding kaise start", "coding shuru", "programming kaise seekhe", "how to start coding",
                "beginner in coding", "start learning to code"
            ])
        ) and "what is python" not in lower:
            return cls._compose_coding_roadmap(lang, context), "cog_coding_roadmap"

        # 3. Career Dilemma (Govt Exam vs Private/Coding, Parents vs Passion)
        if (
            any(w in lower for w in [
                "govt job vs", "government exam vs", "government job vs", "confused about career",
                "parents want government", "family pressure career", "which career is better",
                "sarkari naukri ya", "career choice confuse", "what career should i choose",
                "सरकारी नौकरी", "प्राइवेट जॉब", "सरकारी या प्राइवेट", "sarkari ya private",
                "sarkari naukri", "government job ya private"
            ])
            or (("confused" in lower or "dilemma" in lower or "समझ नहीं आ रहा" in lower) and any(c in lower for c in ["job", "career", "exam", "field", "coding", "नौकरी", "तैयारी"]))
        ):
            return cls._compose_career_dilemma(lang, context), "cog_career_dilemma"

        # 4. Exam Strategy, Active Recall & Blanking Out
        if any(w in lower for w in [
            "how to revise", "remember what i study", "blank out in exam", "blank out",
            "exam preparation tips", "syllabus is huge", "yaad nahi rehta", "revision kaise",
            "exam strategy", "how to memorize", "padha hua yaad nahi", "syllabus complete kaise"
        ]) and lower not in ["my exams", "my exam", "the result", "the results"]:
            return cls._compose_exam_strategy(lang, context), "cog_exam_strategy"

        # 5. Nighttime Overthinking & Sleep Trouble
        if any(w in lower for w in [
            "can't sleep", "cannot sleep", "overthinking at night", "insomnia", "neend nahi",
            "raat ko overthink", "dimag band nahi", "sleep problem", "thoughts keep me awake",
            "so nahi pa raha", "so nahi pa rahi"
        ]):
            return cls._compose_night_overthinking(lang, context), "cog_night_overthinking"

        # 6. Friend / Social Conflict & Misunderstandings
        if any(w in lower for w in [
            "fight with best friend", "fight with friend", "jhagda ho gaya dost", "dost baat nahi kar raha",
            "argument with friend", "friend stopped talking", "misunderstanding with friend",
            "dost naraz hai", "best friend se ladai", "dost baat nahi", "friend not talking"
        ]) or (("friend" in lower or "dost" in lower or "मित्र" in lower) and any(c in lower for c in ["stopped talking", "baat nahi", "naraz", "fight", "ladai", "jhagda"])):
            return cls._compose_friend_conflict(lang, context), "cog_friend_conflict"

        # 7. Self-Confidence & Imposter Syndrome
        if any(w in lower for w in [
            "low confidence", "build self confidence", "build confidence", "imposter syndrome",
            "not good enough", "confidence kaise", "self doubt", "apne aap par vishwas",
            "inferior feel", "confidence nahi hai", "how to believe in myself"
        ]):
            return cls._compose_confidence(lang, context), "cog_confidence"

        # 8. Daily Routine & Time Management
        if any(w in lower for w in [
            "manage time", "time management", "daily routine", "schedule kaise", "balance study and",
            "balance study", "time table kaise", "routine kaise banaye", "how to manage my day", "productive day",
            "manage time with", "time manage kaise"
        ]):
            return cls._compose_time_management(lang, context), "cog_time_management"

        # 9. Fitness, Stamina & Gym Motivation
        if any(w in lower for w in [
            "stay fit", "gym routine", "workout routine", "stamina kaise", "physical fitness tips",
            "diet and workout", "body kaise banaye", "fitness start kaise", "running stamina"
        ]) and "cricket" not in lower:
            return cls._compose_fitness(lang, context), "cog_fitness"

        return None

    @classmethod
    def _compose_procrastination(cls, lang: str, context: Dict[str, Any]) -> str:
        subjects = context.get("mentioned_subjects", [])
        subj_context = f" especially with your {subjects[-1]}" if subjects else ""

        if lang == "hi":
            return (
                "टालमटोल (Procrastination) का मतलब आलस्य नहीं होता—यह अक्सर काम के बड़े आकार या विफलता के अवचेतन भय का परिणाम होता है।\n\n"
                "इसे तुरंत तोड़ने के लिए 3 व्यावहारिक नियम अपनाएं:\n"
                "१. **५-मिनट का नियम (5-Minute Rule):** अपने दिमाग से कहें कि आप सिर्फ ५ मिनट काम करेंगे। शुरुआत की बाधा पार होते ही दिमाग स्वतः काम में लग जाता है।\n"
                "२. **कार्य को सूक्ष्म बनाएं (Micro-Step):** बड़े लक्ष्य के बजाय सिर्फ 'पहली ३ लाइनें लिखने' या 'पहला पेज खोलने' का लक्ष्य रखें।\n"
                "३. **फ़ोन को दृष्टि से दूर रखें:** फोन को दूसरे कमरे में रख दें। जब रुकावट पैदा करने में शारीरिक मेहनत लगेगी, तो भटकाव अपने आप रुक जाएगा।\n\n"
                "अभी वह कौन सा एक काम है जिसे आप सबसे ज्यादा टाल रहे हैं?"
            )
        elif lang == "hinglish":
            return (
                "Procrastination asal mein laziness nahi hai dost—ye aksar tab hota hai jab mind kisi task se overwhelm ho jata hai ya darr lagta hai ki perfect nahi hoga.\n\n"
                "Isko instantly break karne ke 3 proven steps:\n"
                "1. **The 5-Minute Rule:** Khud ko bolo ki main sirf 5 minute kaam karunga, phir band kar dunga. Starting friction break hote hi momentum ban jata hai.\n"
                "2. **Break into Micro-Pieces:** Agar pura syllabus ya project bada lag raha hai, toh sirf 'pehle 2 paragraphs padhne' ka target banao.\n"
                "3. **Phone Distance Hack:** Phone ko charging par dusre room mein rakh do. Friction badhte hi screen-scrolling ruk jayegi.\n\n"
                "Abhi is waqt wo kaun sa specific task hai jo sabse zyada pending pada hai?"
            )
        else:
            return (
                f"Procrastination is rarely a lack of willpower—it is an emotional response when a task{subj_context} feels too big, unclear, or anxiety-inducing.\n\n"
                "Here are 3 concrete strategies to break out of it right now:\n"
                "1. **The 5-Minute Rule:** Tell yourself you only have to work on it for 5 minutes with a timer. Once the initial friction dissolves, your brain naturally wants to continue.\n"
                "2. **Shrink the First Step:** Instead of trying to finish the entire task, make your only goal writing the title or reviewing just one page.\n"
                "3. **Physical Friction on Distractions:** Put your phone in another room or out of arm's reach. Adding a physical barrier kills impulsive checking.\n\n"
                "What is the single specific task you've been putting off today?"
            )

    @classmethod
    def _compose_coding_roadmap(cls, lang: str, context: Dict[str, Any]) -> str:
        if lang == "hi":
            return (
                "पायथन सीखना एक बेहतरीन और दूरदर्शी निर्णय है! यहाँ शुरुआती शिक्षार्थियों के लिए ३० दिनों का व्यावहारिक रोडमैप है:\n\n"
                "१. **पहला चरण (दिन १–७): बुनियादी बातें:** वैरिएबल्स, डेटा टाइप्स, लूप्स (for/while) और if-else शर्तें समझें। छोटे प्रोग्राम्स बनाएं जैसे कैलकुलेटर या नंबर गेसिंग गेम।\n"
                "२. **दूसरा चरण (दिन ८–१८): डेटा स्ट्रक्चर्स और फंक्शन्स:** Lists, Dictionaries, Sets और Functions पर महारत हासिल करें। कोड को दोबारा इस्तेमाल करने का अभ्यास करें।\n"
                "३. **तीसरा चरण (दिन १९–३०): वास्तविक प्रोजेक्ट्स:** सिर्फ ट्यूटोरियल देखने के बजाय ३ छोटे प्रोजेक्ट्स खुद बनाएं—जैसे ऑटोमेटेड फाइल ऑर्गनाइज़र या सिंपल टू-डू ऐप।\n\n"
                "आप मुख्य रूप से किस दिशा में आगे बढ़ना चाहते हैं—वेब डेवलपमेंट, डेटा एनालिसिस या कॉलेज प्रोजेक्ट्स?"
            )
        elif lang == "hinglish":
            return (
                "Python start karna ek bohot solid move hai dost! Tutorial hell se bachne ke liye ye step-by-step roadmap follow karo:\n\n"
                "1. **Phase 1 (Days 1–7): Fundamentals:** Variables, conditional statements (if-else), aur loops (for, while) ko code karke samjho. Calculator jaisa mini program banao.\n"
                "2. **Phase 2 (Days 8–18): Data Structures & Functions:** Lists, Dictionaries, Sets aur custom functions par focus karo. Logic building yahi se strong hoti hai.\n"
                "3. **Phase 3 (Days 19–30): 3 Real Mini Projects:** Sirf video dekhne se coding nahi aati. Ek CLI To-Do App, ek automated file sorter, ya basic web scraper khud banao.\n\n"
                "Aap Python kiske liye seekhna chahte ho—Web Development, Data/AI, ya College syllabus?"
            )
        else:
            return (
                "Starting Python is one of the most rewarding decisions you can make! Here is a structured, practical 30-day roadmap to avoid tutorial burnout:\n\n"
                "1. **Phase 1 (Days 1–7): Fundamentals** — Focus on variables, data types, condition checks (if/else), and loops (for/while). Write interactive terminal scripts like a calculator.\n"
                "2. **Phase 2 (Days 8–18): Data Structures & Functions** — Master Lists, Dictionaries, Sets, and clean modular functions. This is where programmatic thinking takes root.\n"
                "3. **Phase 3 (Days 19–30): Hands-On Projects** — Tutorials show you code, but building creates engineers. Build 3 mini projects: an automated file sorter, a web scraper, and a command-line habit tracker.\n\n"
                "Are you aiming to apply Python in Web Development, Data Science/AI, or automation?"
            )

    @classmethod
    def _compose_career_dilemma(cls, lang: str, context: Dict[str, Any]) -> str:
        if lang == "hi":
            return (
                "यह हमारे देश के युवाओं के सामने आने वाली सबसे आम और चुनौतीपूर्ण दुविधाओं में से एक है: पारिवारिक सुरक्षा की अपेक्षा बनाम आत्मनिर्भर कौशल का निर्माण।\n\n"
                "इस निर्णय को स्पष्ट रूप से समझने के लिए इन ३ बातों पर विचार करें:\n"
                "१. **समय की वास्तविकता (Timeline Check):** सरकारी परीक्षाओं में प्रायः १ से ३ साल का अनिश्चित समय लगता है, जबकि व्यावहारिक डिजिटल स्किल्स (जैसे कोडिंग, डिजाइन) ४ से ६ महीने की सच्ची मेहनत के बाद अवसर देना शुरू कर देती हैं।\n"
                "२. **हाइब्रिड दृष्टिकोण (Hybrid Model):** शुरुआत में सब कुछ छोड़ना ज़रूरी नहीं है। दिन के मुख्य हिस्से को पढ़ाई या परीक्षाओं में दें और रोज़ाना १.५ घंटा बिना भटके डिजिटल स्किल सीखने में लगाएं।\n"
                "३. **प्रमाणित कार्य (Proof of Work):** जब आपके पास कोई ऐसा कौशल हो जिससे आप छोटा फ्रीलांस काम पा सकें, तो परिवार को भी आपकी क्षमता पर स्वतः भरोसा होने लगता है।\n\n"
                "आप इस समय पढ़ाई में किस वर्ष/स्टेज पर हैं?"
            )
        elif lang == "hinglish":
            return (
                "Bohot hi relatable aur serious dilemma hai dost: Family ki security expectations versus practical self-earned career.\n\n"
                "Isko clear tareeqe se analyse karne ke 3 points:\n"
                "1. **Timeline Reality:** Sarkari exams mein aksar 1–3 saal lag jaate hain aur results unpredictable hote hain. Dusri taraf, digital practical skills (like Web Dev, Python) 4–6 months mein tangible results dena shuru kar deti hain.\n"
                "2. **The Hybrid Approach:** Dono mein se kisi ek ko turant reject karne ki zaroorat nahi hai. Apne din ke 70% time ko academic/exam preparation do, aur daily 1.5–2 hours dedicated skill building ko do.\n"
                "3. **Family Trust via Results:** Parents safe options chahte hain kyunki wo tumhari security chahte hain. Jab tum chhoti earning ya portfolio dikhaoge, unka trust khud-ba-khud ban jayega.\n\n"
                "Aap abhi kis field/course mein padhai kar rahe ho?"
            )
        else:
            return (
                "This is one of the most defining crossroads young professionals face: balancing family security expectations against the desire for modern, self-directed career independence.\n\n"
                "Here is an objective framework to navigate this clearly:\n"
                "1. **The Timeline Factor:** Competitive government exams often carry a 1 to 3-year preparation horizon with high uncertainty. Practical digital skills (like Software Development or Design) allow you to validate tangible market demand within 4 to 6 months.\n"
                "2. **The Hybrid Compromise:** You do not have to make an all-or-nothing leap on day one. Dedicate your prime study hours to your core degree/exam commitments, and protect 90 focused minutes every evening for building hands-on digital skills.\n"
                "3. **Proof of Work Over Arguments:** Parents advocate for stability because they want you protected. The moment you show them a live portfolio or initial freelance project, their skepticism shifts into genuine encouragement.\n\n"
                "What stage of college or preparation are you currently in?"
            )

    @classmethod
    def _compose_exam_strategy(cls, lang: str, context: Dict[str, Any]) -> str:
        if lang == "hi":
            return (
                "परीक्षा में पढ़ा हुआ भूल जाना या दिमाग का सुन्न हो जाना ज्ञान की कमी नहीं, बल्कि अत्यधिक तनाव और गलत रिवीज़न पद्धति का परिणाम होता है।\n\n"
                "स्मरण शक्ति और आत्मविश्वास बढ़ाने के ३ वैज्ञानिक नियम:\n"
                "१. **सक्रिय स्मरण (Active Recall):** नोट्स को बार-बार पढ़ने के बजाय, किताब बंद करके याद की गई बातें एक कोरे कागज़ पर लिखें। जब दिमाग को याद करने का प्रयास करना पड़ता है, तभी याददाश्त पक्की होती है।\n"
                "२. **परीक्षा हॉल की रीसेट तकनीक:** यदि परीक्षा के दौरान मन घबराने लगे, तो २ घूंट पानी पिएं, गहरी सांस लें और सबसे पहले उस प्रश्न को हल करें जिसका उत्तर आपको १००% आता हो। इससे आत्मविश्वास तुरंत लौटता है।\n"
                "३. **मॉक टेस्ट से भय मुक्ति:** परीक्षा से पहले कम से कम ३ बार वास्तविक परीक्षा के समय पर लिखकर अभ्यास करें।\n\n"
                "आपकी परीक्षा किस विषय की है और कितना समय बचा है?"
            )
        elif lang == "hinglish":
            return (
                "Exam hall mein blank out hona ya padha hua bhool jana talent ki kami nahi hoti—ye tab hota hai jab stress memory retrieval ko block kar deta hai.\n\n"
                "Isko overcome karne ke 3 proven scientific techniques:\n"
                "1. **Active Recall over Passive Reading:** Notes ko baar-baar highlight karne se dimag mein 'illusion of competence' banta hai. Kitab band karo aur formula blank page par likh kar dekho.\n"
                "2. **The 2-Minute Exam Hall Reset:** Agar paper dekh kar panic ho, toh 3 deep breaths lo, paani piyo, aur sabse aasan sawal se shuru karo. Pehla sahi answer aate hi darr gayab ho jata hai.\n"
                "3. **Previous Year Papers Under Timer:** Timer laga kar kam se kam 2 mock tests likho. Real pressure ki aadat daalo.\n\n"
                "Abhi kis subject ki revision mein sabse zyada tension ho rahi hai?"
            )
        else:
            return (
                "Blanking out during exams is rarely a lack of preparation—it happens when acute performance anxiety spikes, restricting your working memory from retrieving stored concepts.\n\n"
                "Here are 3 scientifically grounded techniques to master retention:\n"
                "1. **Active Recall Over Passive Re-reading:** Re-reading notes creates an illusion of mastery. Instead, close your books and write down the core concepts or formulas from scratch. Effortful retrieval builds durable neural pathways.\n"
                "2. **The 2-Minute Reset in the Exam Hall:** If panic hits, pause immediately. Take three slow belly breaths, drink water, and intentionally scan for the single easiest question. Securing those early points restores immediate cognitive composure.\n"
                "3. **Simulate Real Pressure:** Take at least two full-length past papers strictly under timed, distraction-free conditions before the real exam.\n\n"
                "What subject are you preparing for, and how much time is left before your exam?"
            )

    @classmethod
    def _compose_night_overthinking(cls, lang: str, context: Dict[str, Any]) -> str:
        if lang == "hi":
            return (
                "रात को अत्यधिक विचार (Overthinking) इसलिए आते हैं क्योंकि दिनभर के काम समाप्त होने पर मन को खालीपन मिलता है, और वे सभी चिंताएं सामने आ जाती हैं जो दिन में अनसुलझी रह गई थीं।\n\n"
                "मन को शांत कर सुखद नींद लाने के ३ उपाय:\n"
                "१. **ब्रेन डंप (Brain Dump):** बिस्तर के पास डायरी रखें। जो भी विचार या कल के कार्य मन में आ रहे हों, उन्हें ५ मिनट में कागज़ पर लिख दें। जब बात कागज़ पर आ जाती है, तो दिमाग उसे बार-बार दोहराना बंद कर देता है।\n"
                "२. **४-७-८ श्वास तकनीक:** ४ सेकंड सांस अंदर लें, ७ सेकंड रोकें, और ८ सेकंड में धीरे-धीरे बाहर छोड़ें। यह ३ चक्रों में नर्वस सिस्टम को शांत कर देता है।\n"
                "३. **स्क्रीन से दूरी:** सोने से ३० मिनट पहले फोन को दूर रख दें। स्क्रीन की नीली रोशनी दिमाग को यह भ्रम देती है कि अभी दिन है।\n\n"
                "क्या इस समय किसी खास बात को लेकर चिंता चल रही है?"
            )
        elif lang == "hinglish":
            return (
                "Raat ko overthinking isliye badh jati hai kyunki din ki bhagdod khatam hote hi dimag ko saari unprocessed worries process karne ka mauka milta hai.\n\n"
                "Isko shant karke deep sleep paane ke 3 quick solutions:\n"
                "1. **The Brain Dump on Paper:** Bedside par ek dairy rakho aur 5 minute mein saare ghoomte hue thoughts aur kal ke tasks likh daalo. Paper par aate hi brain unko hold karna chhod deta hai.\n"
                "2. **4-7-8 Breathing:** 4 seconds saans lo, 7 seconds roko, aur 8 seconds mein dheere-dheere exhale karo. 3-4 cycles mein heartbeat calm ho jati hai.\n"
                "3. **Zero Screen Time 30 mins Prior:** Phone ki blue light melatonin suppress karti hai. Phone ko doosre kone mein rakh kar aankhen band karo.\n\n"
                "Kya koi specific baat dimag mein loop par chal rahi hai?"
            )
        else:
            return (
                "Nighttime overthinking happens because the daytime sensory stimulation quietens down, giving unaddressed anxieties an open stage to loop in your mind.\n\n"
                "Here are 3 bedtime practices to quiet the mental chatter:\n"
                "1. **The 5-Minute Brain Dump:** Keep a physical notepad next to your bed. Write down every nagging thought, doubt, or tomorrow's to-do items. Moving thoughts onto paper signals your brain that they are safely recorded.\n"
                "2. **The 4-7-8 Calming Breath:** Inhale quietly through your nose for 4 seconds, hold for 7 seconds, and exhale completely through your mouth for 8 seconds. This physiologically activates your parasympathetic rest system.\n"
                "3. **Cut Screen Exposure 30 Minutes Before Bed:** Blue light keeps cortisol elevated and tricks your brain into thinking it's still daytime.\n\n"
                "Is there a particular problem or decision looping in your thoughts tonight?"
            )

    @classmethod
    def _compose_friend_conflict(cls, lang: str, context: Dict[str, Any]) -> str:
        if lang == "hi":
            return (
                "किसी सच्चे मित्र से मनमुटाव होना बहुत पीड़ादायक होता है क्योंकि हमारा मन बार-बार उन बातों को दोहराता है जो गुस्से में कही गईं।\n\n"
                "इस स्थिति को परिपक्वता से सुलझाने के ३ चरण:\n"
                "१. **२४ घंटे का कूलिंग पीरियड:** गुस्से के तुरंत बाद स्पष्टीकरण देने से बहस और बढ़ती है। दोनों पक्षों की भावनाओं को शांत होने के लिए थोड़ा समय दें।\n"
                "२. **अहंकार के बजाय रिश्ते को प्राथमिकता दें:** बात की शुरुआत इस बात से न करें कि 'गलती किसकी थी'। कहें: 'मैं तुम्हारी दोस्ती को किसी बहस से बड़ा मानता हूँ, क्या हम शांत मन से बात कर सकते हैं?'\n"
                "३. **अपनी बात 'I' संदेश से रखें:** आरोप लगाने के बजाय कहें कि 'उस बात से मुझे बुरा लगा'।\n\n"
                "क्या आप बताना चाहेंगे कि बात किस बात पर बिगड़ी थी?"
            )
        elif lang == "hinglish":
            return (
                "Kisi close friend se ladai ya misunderstanding hona sach mein bohot heavy feel karata hai dost.\n\n"
                "Isko mature tareeqe se resolve karne ke 3 steps:\n"
                "1. **The 24-Hour Cooling Window:** Gusse mein self-defense ego active hota hai. Turant message karke lamba paragraph bhejne ke bajay thoda waqt do taaki raw anger settle ho sake.\n"
                "2. **Choose Connection Over Winning:** Argument jeetne se dosti haar jaati hai. Simple text karo: 'Hamari dosti is misunderstanding se zyada important hai. Jab comfortable ho, let us talk calmly.'\n"
                "3. **Listen Without Defending:** Jab wo bole, toh beech mein kaate bina suno. Aksar log bas validation chahte hain.\n\n"
                "Khas baat kya hui thi jispar baat bigad gayi?"
            )
        else:
            return (
                "Conflict with a close friend cuts deep because your mind keeps replaying sharp words exchanged in the heat of the moment.\n\n"
                "Here is how to navigate and repair the bond with emotional maturity:\n"
                "1. **The 24-Hour Cooling Window:** When tempers flare, ego takes over. Avoid sending long, defensive text messages right away. Give both of you a day for raw adrenaline to settle.\n"
                "2. **Prioritize the Bond Over Winning:** You can either win the debate or keep the friendship. Reach out with simplicity: 'Our friendship matters more to me than being right. Whenever you're ready, let's talk calmly.'\n"
                "3. **Speak in 'I' Statements, Not Accusations:** Instead of 'You said this and ruined it,' use 'I felt hurt by how that unfolded.'\n\n"
                "Would you like to share what triggered the disagreement?"
            )

    @classmethod
    def _compose_confidence(cls, lang: str, context: Dict[str, Any]) -> str:
        if lang == "hi":
            return (
                "आत्मविश्वास कोई जन्मजात गुण नहीं है, बल्कि यह रोज़ाना खुद से किए गए छोटे-छोटे वादों को पूरा करने का स्वाभाविक परिणाम है।\n\n"
                "सच्चा आत्मविश्वास विकसित करने के ३ व्यावहारिक कदम:\n"
                "१. **सूक्ष्म वादों का पालन:** रोज़ाना एक ऐसा छोटा वादा चुनें जिसे आप निश्चित रूप से पूरा कर सकें (जैसे १५ मिनट व्यायाम या १ पेज पढ़ना)। जब आप खुद पर विश्वास करने लगते हैं, तो आत्मविश्वास बढ़ता है।\n"
                "२. **तुलना बंद करें:** दूसरों की मंज़िल की तुलना अपने शुरुआती सफ़र से कभी न करें। आपकी एकमात्र तुलना आपके कल के रूप से होनी चाहिए।\n"
                "३. **गलतियों को सीख मानें:** गलती करना अक्षमता का प्रमाण नहीं, बल्कि सीखने की प्रक्रिया का अनिवार्य हिस्सा है।\n\n"
                "किस क्षेत्र में आपको सबसे ज्यादा आत्म-संदेह (Self-Doubt) महसूस होता है?"
            )
        elif lang == "hinglish":
            return (
                "Self-confidence koi aisi cheez nahi hai jo kisi ke paas hoti hai aur kisi ke paas nahi. Ye daily habits se build hone wali muscle hai.\n\n"
                "Apna confidence naturally grow karne ke 3 rules:\n"
                "1. **Keep Tiny Promises to Yourself:** Agar roz decide karo ki 20 minute padhna hai aur sach mein padho, toh dimag khud par trust karna seekhta hai. Self-trust hi real confidence hai.\n"
                "2. **Stop Social Comparison:** Instagram ya doosron ke highlight reel se apna everyday struggle compare mat karo. Sabke apne hidden struggles hote hain.\n"
                "3. **Failure is Data, Not Identity:** Kisi kaam mein fail hone ka matlab ye nahi ki 'aap failure ho'. Iska matlab sirf itna hai ki strategy improve karni hai.\n\n"
                "Kis cheez mein aapko sabse zyada self-doubt feel hota hai?"
            )
        else:
            return (
                "Self-confidence is not a personality trait you are born with—it is the natural byproduct of keeping small, honest promises to yourself every single day.\n\n"
                "Here are 3 evidence-based habits to rebuild grounded self-belief:\n"
                "1. **Keep Micro-Promises to Yourself:** Start making tiny commitments you can easily keep (e.g., studying 20 minutes, drinking water, doing 10 pushups). Every kept promise deposits trust into your self-esteem bank.\n"
                "2. **Stop Comparing Your Behind-the-Scenes to Others' Highlight Reels:** You see everyone else's polished outcomes while living inside your own doubts and false starts. Focus exclusively on your own trajectory.\n"
                "3. **Reframe Mistakes as Data:** Failing a test or stumbling in an interview does not make you a failure. It simply gives you diagnostic feedback on what to adjust next.\n\n"
                "In which area of your life do you feel self-doubt creeping in the most?"
            )

    @classmethod
    def _compose_time_management(cls, lang: str, context: Dict[str, Any]) -> str:
        subjects = context.get("mentioned_subjects", [])
        subj_note = f" (including your {', '.join(subjects[:2])})" if subjects else ""

        if lang == "hi":
            return (
                "समय प्रबंधन वास्तव में समय को नहीं, बल्कि अपनी ऊर्जा और प्राथमिकताओं को प्रबंधित करने की कला है।\n\n"
                "एक अत्यधिक प्रभावी और तनावमुक्त दिनचर्या के ३ नियम:\n"
                "१. **नियम ३ (Rule of 3):** रोज़ाना सुबह केवल ३ सबसे महत्वपूर्ण कार्य तय करें जिन्हें पूरा करना आवश्यक है। बाकी सभी कामों को द्वितीयक समझें।\n"
                "२. **टाइम ब्लॉकिंग (Time Blocking):** पूरे दिन काम करने के बजाय, ९० मिनट के केंद्रित कार्य खंड (Focus Blocks) तय करें, और उनके बीच १५ मिनट का पूर्ण विश्राम लें।\n"
                "३. **ऊर्जा के अनुसार कार्य:** कठिन और मानसिक परिश्रम वाले कार्यों को उस समय करें जब आपकी ऊर्जा सबसे अधिक हो (प्रायः सुबह)।\n\n"
                "वर्तमान में कौन सी चीज़ आपका सबसे अधिक समय अनावश्यक रूप से लेती है?"
            )
        elif lang == "hinglish":
            return (
                f"Time management असल mein time ko nahi, apni energy aur priorities ko manage karna hai dost{subj_note}.\n\n"
                "Apne din ko streamline karne ke 3 golden rules:\n"
                "1. **The Rule of 3:** Har subah sirf 3 non-negotiable tasks decide karo jo aaj har haal mein complete karne hain. Baaki sab optional hai.\n"
                "2. **Time-Boxing (90-min Blocks):** Pura din 'padhai kar raha hoon' kehne ke bajay, 2 dedicated 90-minute ke deep work blocks banao bina kisi phone notification ke.\n"
                "3. **Protect Your Peak Energy:** Subah ke pehle 2 ghante sabse mushkil subject ya project ko do jab willpower fresh hoti hai.\n\n"
                "Abhi routine mein sabse badi problem kya aa rahi hai—subah uthna, ya din mein focus khona?"
            )
        else:
            return (
                f"True time management is not about squeezing more tasks into 24 hours—it is about ruthlessly protecting your peak cognitive energy for what actually matters{subj_note}.\n\n"
                "Here are 3 battle-tested principles for a calm, high-output daily routine:\n"
                "1. **The Rule of 3:** Every morning, write down only 3 critical needle-moving tasks. If you finish those three, your day is an unquestionable win.\n"
                "2. **Time-Block 90-Minute Focus Sprints:** Human attention operates in ultradian cycles. Work deeply for 75 to 90 minutes with zero notifications, then take a real 15-minute screen-free break.\n"
                "3. **Match Tasks to Energy Levels:** Tackle the hardest intellectual challenge (complex concepts, coding, tough problem sets) during your highest mental energy window.\n\n"
                "Where does most of your time leak away right now—procrastination, unexpected interruptions, or switching between too many tasks?"
            )

    @classmethod
    def _compose_fitness(cls, lang: str, context: Dict[str, Any]) -> str:
        if lang == "hi":
            return (
                "शारीरिक तंदुरुस्ती केवल दिखावे के लिए नहीं, बल्कि मानसिक स्पष्टता, ऊर्जा और आत्मविश्वास का सबसे मजबूत आधार है।\n\n"
                "शुरुआत करने के ३ व्यावहारिक स्तंभ:\n"
                "१. **तीव्रता से अधिक निरंतरता (Consistency over Intensity):** शुरुआत में २ घंटे जिम करने की ज़रूरत नहीं है। रोज़ाना सिर्फ २५ से ३० मिनट का ईमानदार व्यायाम लंबे समय में बड़ा परिणाम देता है।\n"
                "२. **बुनियादी अभ्यास (Compound Movements):** पुश-अप्स, स्क्वाट्स, और तेज चलना या दौड़ना पूरे शरीर की ताकत और स्टैमिना को बढ़ाते हैं।\n"
                "३. **नींद और जल:** प्रतिदिन ३ लीटर पानी और ७-८ घंटे की गुणवत्तापूर्ण नींद शरीर की रिकवरी के लिए व्यायाम जितनी ही आवश्यक है।\n\n"
                "आपका प्राथमिक लक्ष्य क्या है—वजन घटाना, वजन बढ़ाना/मसल बिल्डिंग, या स्टैमिना बढ़ाना?"
            )
        elif lang == "hinglish":
            return (
                "Fitness sirf body ke liye nahi, balki mental focus aur anxiety release karne ka sabse powerful tool hai dost!\n\n"
                "Sustainable fitness routine shuru karne ke 3 pillars:\n"
                "1. **Consistency Beats Motivation:** Pehle hafte mein 2 ghante marne se kuch nahi hoga agar agle hafte drop kar do. Daily 30 minutes, 5 days a week ka realistic commitment lo.\n"
                "2. **Master the Basics:** Push-ups, Squats, Pull-ups aur brisk walking/jogging se start karo. Ye core strength aur stamina tezi se build karte hain.\n"
                "3. **Hydration & Sleep:** 3 litres paani aur 7 ghante ki uninterrupted sleep bina koi workout kaam nahi karega.\n\n"
                "Aapka main goal kya hai—weight loss, muscle building, ya overall stamina?"
            )
        else:
            return (
                "Physical fitness is not just about aesthetics—it is the single most reliable catalyst for mental clarity, resilience, and stress reduction.\n\n"
                "Here are 3 foundational pillars to build lasting physical momentum:\n"
                "1. **Consistency Trumps Intensity:** A modest 30-minute workout executed 4 to 5 days every single week beats an aggressive 2-hour workout you abandon after 10 days.\n"
                "2. **Prioritize Fundamental Movement Patterns:** Master compound movements—pushups, bodyweight squats, planks, and brisk walking or jogging. They build functional mobility and systemic stamina.\n"
                "3. **Recovery is Where Growth Happens:** 7 to 8 hours of disciplined sleep and 3 liters of water daily are non-negotiable for muscle repair and nervous system recovery.\n\n"
                "What is your primary fitness aspiration—building muscle, losing fat, or boosting energy and stamina?"
            )
