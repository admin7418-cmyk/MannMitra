import re
from services.chatbot_service import get_chatbot_service
from services.sentiment_service import analyze
from services.safety_service import needs_human_support, response
from services.gita_service import recommend

FRIENDSHIP_KEYWORDS = [
    'friend', 'friends', 'be my friend', 'become my friend', 'can we be friends',
    'will you be my friend', 'will you become my friend', 'are you my friend',
    'best friend', 'companion', 'be with me', 'talk to me', 'who are you',
    'tell me about you', 'tell me about yourself', 'are you real', 'do you care',
    'can i trust you', 'make friends', 'friendship', 'bestie', 'buddy',
    'दोस्त', 'मित्र', 'सखा', 'दोस्ती', 'मित्र बनोगे', 'दोस्त बनोगे',
    'क्या तुम मेरे दोस्त बनोगे', 'क्या आप मेरे मित्र बनेंगे', 'मेरे साथ रहो',
    'मुझसे बात करो', 'तुम कौन हो', 'आप कौन हैं', 'क्या हम दोस्त बन सकते हैं',
    'सच्चा दोस्त', 'सच्चा मित्र', 'मित्रता',
    'dost', 'dosti', 'mitra', 'friend banoge', 'dost banoge', 'kya tum mere dost banoge',
    'kya hum dost ban sakte hain', 'mere dost ban jao', 'kya tum mere friend ho',
    'tum kaun ho', 'aap kaun ho', 'mujhse baat karo', 'saccha dost', 'pakka dost',
    'mere friend banoge', 'friend ban jao'
]

LONELY_KEYWORDS = [
    'lonely', 'alone', 'no one understands', 'have no friends', 'nobody likes me',
    'feeling lonely', 'left out', 'all alone', 'isolated', 'i am lonely', 'no one cares',
    'अकेला', 'अकेलापन', 'कोई नहीं समझता', 'मेरा कोई दोस्त नहीं', 'अकेला महसूस', 'अकेली',
    'akela', 'akelapan', 'koi nahi samajhta', 'mera koi friend nahi', 'akela feel', 'akeli'
]

CASUAL_KEYWORDS = [
    'hi', 'hello', 'hey', 'good morning', 'good evening', 'good night', 'how are you', 'what is up', 'sup',
    'नमस्ते', 'नमस्कार', 'प्रणाम', 'कैसे हो', 'कैसी हो', 'शुभ प्रभात', 'शुभ रात्रि',
    'namaste', 'kaise ho', 'kaisa hai', 'kya hal hai', 'kya haal hai', 'kaisa chal raha hai'
]

POSITIVE_KEYWORDS = [
    'thank', 'thanks', 'great', 'awesome', 'happy', 'good', 'better', 'peaceful', 'relieved', 'grateful',
    'धन्यवाद', 'शुक्रिया', 'अच्छा', 'बहुत अच्छा', 'खुश', 'प्रसन्न', 'राहत', 'शांति',
    'shukriya', 'dhanyawad', 'accha', 'mast', 'badhiya', 'khush', 'sukoon', 'relieved'
]

PROBLEM_KEYWORDS = [
    'stress', 'tension', 'sad', 'fear', 'anxiety', 'overthink', 'overthinking',
    'exam', 'study', 'studies', 'failure', 'fail', 'motivation', 'pressure', 'confused', 'confusion',
    'angry', 'anger', 'focus', 'worried', 'worry', 'scared', 'tired', 'burden',
    'तनाव', 'चिंता', 'उदासी', 'डर', 'भय', 'परीक्षा', 'पढ़ाई', 'विफलता',
    'असफल', 'प्रेरणा', 'दबाव', 'गुस्सा', 'क्रोध', 'एकाग्रता', 'थकान', 'व्याकुल',
    'chinta', 'pareshan', 'pareshani', 'darr', 'udas', 'padhai', 'pariksha',
    'marks', 'gussa', 'thak gaya', 'thak gayi', 'himmat', 'confuse', 'overthink'
]

def generate_reply(message, history=None, lang='en', user_id=None):
    """
    Main conversational entrypoint delegating to ChatbotService.
    Preserves existing contract for all routes and unit tests.
    """
    service = get_chatbot_service()
    result = service.process_message(message, user_id=user_id or "default_user", explicit_lang=lang)
    return result
