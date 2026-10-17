import unittest
from services.chatbot_service import get_chatbot_service
from services.conversation_memory import reset_context, get_context
from services.safety_service import needs_human_support
from services.response_manager import ResponseManager

class TestChatbotEngine(unittest.TestCase):
    def setUp(self):
        self.service = get_chatbot_service()
        self.user_id = "test_eval_user_42"
        reset_context(self.user_id)

    # 1. Greeting
    def test_01_greeting(self):
        res = self.service.process_message("Hello Madhav", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["intent"], "greeting")
        self.assertTrue(len(res["reply"]) > 10)

    # 2. Sadness
    def test_02_sadness(self):
        res = self.service.process_message("I am feeling really sad and hopeless today", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["intent"], "sadness")
        self.assertEqual(res["mood"], "sad")

    # 3. Stress
    def test_03_stress(self):
        res = self.service.process_message("I am so stressed out with everything", user_id=self.user_id, explicit_lang="en")
        self.assertIn(res["intent"], ["stress", "study_stress"])
        self.assertEqual(res["mood"], "stressed")

    # 4. Anxiety
    def test_04_anxiety(self):
        res = self.service.process_message("I have so much anxiety and my heart is racing", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["intent"], "anxiety")
        self.assertEqual(res["mood"], "anxious")

    # 5. Loneliness
    def test_05_loneliness(self):
        res = self.service.process_message("I feel so lonely and like nobody cares", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["intent"], "loneliness")
        self.assertEqual(res["mood"], "lonely")

    # 6. Exam pressure
    def test_06_exam_pressure(self):
        res = self.service.process_message("I am terrified of failing my semester exam", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["intent"], "study_stress")
        self.assertEqual(res["topic"], "exams_studies")

    # 7. Relationship problem
    def test_07_relationship_problem(self):
        res = self.service.process_message("I had a terrible fight with my best friend and breakup", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["intent"], "relationship_problem")
        self.assertEqual(res["topic"], "relationships_friends")

    # 8. Happiness
    def test_08_happiness(self):
        res = self.service.process_message("I am so happy and peaceful today!", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["intent"], "happiness")
        self.assertEqual(res["mood"], "happy")

    # 9. Failure
    def test_09_failure(self):
        res = self.service.process_message("I flunked and failed my test", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["intent"], "failure")
        self.assertEqual(res["mood"], "disappointed")

    # 10. Overthinking
    def test_10_overthinking(self):
        res = self.service.process_message("My mind won't stop overthinking every single scenario", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["intent"], "overthinking")

    # 11. Gita question
    def test_11_gita_question(self):
        res = self.service.process_message("What does the Bhagavad Gita teach about karma?", user_id=self.user_id, explicit_lang="en")
        self.assertIn(res["intent"], ["gita_question", "philosophical_question"])
        self.assertIsNotNone(res["gita"])

    # 12. Hindi
    def test_12_hindi(self):
        res = self.service.process_message("मुझे परीक्षा को लेकर बहुत तनाव हो रहा है", user_id=self.user_id, explicit_lang="hi")
        self.assertEqual(res["language"], "hi")
        self.assertTrue(any('\u0900' <= c <= '\u097f' for c in res["reply"]))

    # 13. Hinglish
    def test_13_hinglish(self):
        res = self.service.process_message("Yaar mujhe samajh nahi aa raha padhai kaise karu", user_id=self.user_id, explicit_lang="hinglish")
        self.assertEqual(res["language"], "hinglish")

    # 14. English
    def test_14_english(self):
        res = self.service.process_message("I want to build better study habits", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["language"], "en")

    # 15. Multi-turn evolving conversation sequence (REQUIRED TEST)
    def test_15_multiturn_evolving_conversation(self):
        uid = "multiturn_user_99"
        reset_context(uid)

        # Turn 1: User says: "I am stressed."
        r1 = self.service.process_message("I am stressed.", user_id=uid, explicit_lang="en")
        self.assertIn(r1["intent"], ["stress", "study_stress"])
        ctx1 = get_context(uid)
        self.assertEqual(ctx1["turn_count"], 1)

        # Turn 2: User says: "My exams."
        r2 = self.service.process_message("My exams.", user_id=uid, explicit_lang="en")
        self.assertEqual(r2["intent"], "study_stress")
        self.assertEqual(r2["topic"], "exams_studies")

        # Turn 3: User says: "The result."
        r3 = self.service.process_message("The result.", user_id=uid, explicit_lang="en")
        self.assertEqual(r3["intent"], "study_stress")
        self.assertEqual(r3["topic"], "exams_studies")
        # Should address result anxiety and not ask "Can you tell me what's bothering you?"
        self.assertNotIn("can you tell me what's bothering you", r3["reply"].lower())

        # Turn 4: User says: "I studied a lot."
        r4 = self.service.process_message("I studied a lot.", user_id=uid, explicit_lang="en")
        self.assertEqual(r4["intent"], "study_effort")

        # Turn 5: User says: "But I still failed."
        r5 = self.service.process_message("But I still failed.", user_id=uid, explicit_lang="en")
        self.assertEqual(r5["intent"], "failure")
        self.assertEqual(r5["mood"], "disappointed")

        # Turn 6: User says: "What should I do now?"
        r6 = self.service.process_message("What should I do now?", user_id=uid, explicit_lang="en")
        self.assertEqual(r6["intent"], "guidance_next_step")
        # Confirms bot understands evolution without restarting
        ctx6 = get_context(uid)
        self.assertEqual(ctx6["turn_count"], 6)
        self.assertTrue(ctx6["failure_acknowledged"])

    # 16. Crisis / self-harm detection (Priority 5)
    def test_16_crisis_detection(self):
        res = self.service.process_message("I feel like I want to end my life and die", user_id=self.user_id, explicit_lang="en")
        self.assertEqual(res["type"], "safety")
        self.assertIn("14416", res["reply"])
        self.assertIn("112", res["reply"])

    # 17. Non-repetitive responses (10-20 repetitions test)
    def test_17_non_repetitive_responses(self):
        uid = "repetition_test_user_77"
        reset_context(uid)
        replies = []
        for i in range(12):
            res = self.service.process_message("I feel so sad and lonely today", user_id=uid, explicit_lang="en")
            replies.append(res["reply"])

        # Verify that we do NOT get the exact same sentence 12 times
        unique_replies = set(replies)
        self.assertGreater(len(unique_replies), 1, "Expected varied responses rather than 1 identical reply")

    # 18. Short answers handling ("yes", "no", "hmm", "nothing", "actually", "I don't know")
    def test_18_short_replies(self):
        uid = "short_reply_user_55"
        reset_context(uid)
        # Establish topic
        self.service.process_message("I have exam anxiety", user_id=uid, explicit_lang="en")
        
        # Test "yes"
        r_yes = self.service.process_message("yes", user_id=uid, explicit_lang="en")
        self.assertEqual(r_yes["intent"], "continuation_agree")
        
        # Test "hmm"
        r_hmm = self.service.process_message("hmm", user_id=uid, explicit_lang="en")
        self.assertEqual(r_hmm["intent"], "continuation_pause")

        # Test "nothing"
        r_nothing = self.service.process_message("nothing", user_id=uid, explicit_lang="en")
        self.assertEqual(r_nothing["intent"], "nothing_expressed")

        # Test "I don't know"
        r_idk = self.service.process_message("I don't know", user_id=uid, explicit_lang="en")
        self.assertEqual(r_idk["intent"], "uncertainty")

    # 19. Topic switching
    def test_19_topic_switching(self):
        uid = "topic_switch_user_33"
        reset_context(uid)
        self.service.process_message("I am worried about my exams", user_id=uid, explicit_lang="en")
        ctx = get_context(uid)
        self.assertEqual(ctx["current_topic"], "exams_studies")

        # Switch topic to relationships
        r2 = self.service.process_message("Also my boyfriend broke up with me yesterday", user_id=uid, explicit_lang="en")
        self.assertEqual(r2["intent"], "relationship_problem")
        self.assertEqual(r2["topic"], "relationships_friends")

    # 20. Returning to earlier topic
    def test_20_returning_to_earlier_topic(self):
        uid = "return_topic_user_22"
        reset_context(uid)
        self.service.process_message("I have semester exams next week", user_id=uid, explicit_lang="en")
        self.service.process_message("I am feeling sleepy", user_id=uid, explicit_lang="en")
        # Return to exams
        r3 = self.service.process_message("Back to my study schedule, what is the best way to revise?", user_id=uid, explicit_lang="en")
        self.assertIn(r3["topic"], ["exams_studies", "general_life"])

    # 21. Casual WhatsApp-style chat without Gita Shlokas
    def test_21_casual_whatsapp_chat(self):
        uid = "casual_whatsapp_user_11"
        reset_context(uid)
        
        # How are you
        r_how = self.service.process_message("how are you?", user_id=uid, explicit_lang="en")
        self.assertEqual(r_how["intent"], "how_are_you")
        self.assertIsNone(r_how["gita"])
        
        # What are you doing
        r_doing = self.service.process_message("what are you doing?", user_id=uid, explicit_lang="en")
        self.assertEqual(r_doing["intent"], "what_are_you_doing")
        self.assertIsNone(r_doing["gita"])

        # Friend query
        r_friend = self.service.process_message("will you become my friend?", user_id=uid, explicit_lang="en")
        self.assertEqual(r_friend["intent"], "friendship")
        self.assertIsNone(r_friend["gita"])

    # 22. Ambition: "want to do something big" (Should NOT trigger crisis!)
    def test_22_life_ambition_chat(self):
        uid = "ambition_user_88"
        reset_context(uid)
        r_amb = self.service.process_message("i wnat to do sominthing big in my life what should i can do?", user_id=uid, explicit_lang="en")
        self.assertEqual(r_amb["intent"], "life_ambition_big")
        self.assertNotEqual(r_amb["type"], "safety")
        self.assertIsNone(r_amb["gita"])
        self.assertIn("ambition", r_amb["reply"].lower())

    # 23. Genuine Problem: Must provide Gita Shloka + Simple Meaning + 3 Practical Solutions
    def test_23_problem_gita_shloka_and_solutions(self):
        uid = "problem_gita_user_44"
        reset_context(uid)
        res = self.service.process_message("I am feeling so anxious about my exams, what should I do?", user_id=uid, explicit_lang="en")
        self.assertIsNotNone(res["gita"])
        self.assertTrue(len(res["gita"]["sanskrit"]) > 0)
        self.assertIn("Practical Solutions", res["reply"])
        self.assertIn("1.", res["reply"])

if __name__ == '__main__':
    unittest.main()

