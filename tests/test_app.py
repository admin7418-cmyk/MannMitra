import unittest
from app import app
from services.chat_service import generate_reply
from services.safety_service import needs_human_support
from services.gita_service import recommend, search
from database.connection import get_db_status
from models.habit_model import get_badges

class MannMitraTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_home(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

    def test_analyze_api(self):
        res = self.client.post("/api/analyze", json={"text": "I am having a wonderful day"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("mood", data)
        self.assertIn("score", data)
        self.assertEqual(data["mood"], "Positive")

    def test_chat_english(self):
        res = generate_reply("I feel so stressed about my exams", lang="en")
        self.assertEqual(res["type"], "gita")
        self.assertIn("Gita", res["reply"])
        self.assertIsNotNone(res["gita"])

    def test_chat_hindi(self):
        res = generate_reply("मुझे परीक्षा को लेकर बहुत चिंता हो रही है", lang="hi")
        self.assertEqual(res["type"], "gita")
        self.assertIn("मार्गदर्शन", res["reply"])
        self.assertIsNotNone(res["gita"])

    def test_chat_hinglish(self):
        res = generate_reply("Bohot overthinking ho rahi hai kya karu", lang="hinglish")
        self.assertEqual(res["type"], "gita")
        self.assertIn("Shlok", res["reply"])
        self.assertIsNotNone(res["gita"])

    def test_safety_detection_multilingual(self):
        # English crisis
        self.assertTrue(needs_human_support("I want to end my life"))
        # Hindi crisis
        self.assertTrue(needs_human_support("मैं मरना चाहता हूँ"))
        # Hinglish crisis
        self.assertTrue(needs_human_support("Mujhe suicide karna hai ab aur nahi sah sakta"))
        # Non-crisis normal text
        self.assertFalse(needs_human_support("I am going to study math now"))

    def test_gita_service_multilingual(self):
        v_en = recommend("exam stress", lang="en")
        self.assertEqual(v_en["active_lang"], "en")
        self.assertIn("meaning_en", v_en)

        v_hi = recommend("exam stress", lang="hi")
        self.assertEqual(v_hi["active_lang"], "hi")
        self.assertIn("meaning_hi", v_hi)

        v_hng = recommend("exam stress", lang="hinglish")
        self.assertEqual(v_hng["active_lang"], "hinglish")
        self.assertIn("meaning_hinglish", v_hng)

    def test_database_status(self):
        status = get_db_status()
        self.assertIn("engine", status)
        self.assertIn("mode", status)
        self.assertTrue(status["connected"])

    def test_gamification_badges(self):
        badges = get_badges(journals_count=3, completed_habits=5, streak=3)
        unlocked = [b["id"] for b in badges if b["unlocked"]]
        self.assertIn("first_reflection", unlocked)
        self.assertIn("mindful_starter", unlocked)
        self.assertIn("streak_3", unlocked)
        self.assertIn("habit_champ", unlocked)
        self.assertIn("wisdom_seeker", unlocked)

    def test_calm_page(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'test_user_1'
        res = self.client.get("/calm")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Calm Mode", res.data)

    def test_gita_page_multilingual(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'test_user_1'
        # English
        res_en = self.client.get("/gita?lang=en")
        self.assertEqual(res_en.status_code, 200)
        # Hindi
        res_hi = self.client.get("/gita?lang=hi")
        self.assertEqual(res_hi.status_code, 200)
        # Hinglish
        res_hg = self.client.get("/gita?lang=hinglish")
        self.assertEqual(res_hg.status_code, 200)

    def test_api_chat_multilingual(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'test_user_1'
        res = self.client.post("/api/chat", json={
            "message": "Stress ho raha hai bohot",
            "language": "hinglish"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("reply", data)
        self.assertEqual(data.get("language"), "hinglish")

    def test_admin_and_profile_routes(self):
        # 1. Normal user without admin privileges is blocked from /admin and redirected to admin login
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'test_user_1'
            sess['role'] = 'user'
        res_admin_blocked = self.client.get("/admin")
        self.assertEqual(res_admin_blocked.status_code, 302)
        self.assertIn("/admin/login", res_admin_blocked.headers.get("Location", ""))

        # 2. Admin login page is accessible
        res_admin_login_page = self.client.get("/admin/login")
        self.assertEqual(res_admin_login_page.status_code, 200)

        # 3. Successful admin login with official credentials (admin / Admin@118119)
        res_post_admin = self.client.post("/admin/login", data={
            "username": "admin",
            "password": "Admin@118119"
        }, follow_redirects=True)
        self.assertEqual(res_post_admin.status_code, 200)
        self.assertIn(b"ADMINISTRATOR MODE", res_post_admin.data)

        # 4. Profile page accessible by user
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'test_user_1'
        res_profile = self.client.get("/profile")
        self.assertEqual(res_profile.status_code, 200)

    def test_user_account_case_insensitivity_and_identifier(self):
        from services.auth_service import register, authenticate
        from models.user_model import find_by_identifier, find_by_email
        from datetime import datetime
        import uuid

        random_suffix = uuid.uuid4().hex[:6]
        test_email = f"TestUser_{random_suffix}@Example.com"
        test_user = f"Student_{random_suffix}"
        test_pass = "SecurePass123"

        # Register
        register(test_user, test_email, test_pass, datetime.now().isoformat())

        # Test login via lowercase email
        user_by_email = authenticate(test_email.lower(), test_pass)
        self.assertIsNotNone(user_by_email)
        self.assertEqual(user_by_email['email'].lower(), test_email.lower())

        # Test login via username
        user_by_name = authenticate(test_user, test_pass)
        self.assertIsNotNone(user_by_name)
        self.assertEqual(user_by_name['name'], test_user)

    def test_community_interactions(self):
        from models.community_model import create, recent, like_post, report_post
        from datetime import datetime
        now = datetime.now().isoformat()
        create('test_user_1', 'Staying mindful and calm today! 🌱', now)
        posts = recent(10)
        self.assertGreater(len(posts), 0)
        post_id = posts[0]['id']
        like_post(post_id)
        report_post(post_id)

    def test_habit_workflow(self):
        from models.habit_model import create, all_for_user, toggle, delete_habit
        from datetime import datetime
        now = datetime.now().isoformat()
        create('test_user_1', 'Meditate 10 mins', now)
        habits = all_for_user('test_user_1')
        self.assertGreater(len(habits), 0)
        hid = habits[0]['id']
        toggle(hid, 'test_user_1')
        delete_habit(hid, 'test_user_1')

    def test_ask_madhav_page_and_logo(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'test_user_1'
        res = self.client.get("/chat")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        self.assertIn("Ask Madhav", html)
        self.assertIn("logo.png", html)
        self.assertIn("dock-send-btn", html)
        self.assertIn("mic-btn", html)
        self.assertIn('data-theme="peace"', html)

    def test_friendship_conversation_multilingual(self):
        # English: Will you become my friend?
        res_en = generate_reply("will you become my friend", lang="en")
        self.assertEqual(res_en["type"], "friendship")
        self.assertIn("love to be your friend", res_en["reply"])

        # Hinglish: kya tum mere dost banoge?
        res_hg = generate_reply("kya tum mere dost banoge", lang="hinglish")
        self.assertEqual(res_hg["type"], "friendship")
        self.assertIn("saccha friend", res_hg["reply"])

        # Hindi: क्या आप मेरे मित्र बनेंगे?
        res_hi = generate_reply("क्या आप मेरे मित्र बनेंगे", lang="hi")
        self.assertEqual(res_hi["type"], "friendship")
        self.assertIn("सच्चा दोस्त", res_hi["reply"])

    def test_theme_peace_css_contrast(self):
        with open('static/css/style.css', 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('html[data-theme=peace] h1', css)
        self.assertIn('html[data-theme=peace] p', css)
        self.assertIn('html[data-theme=peace] label', css)
        self.assertIn('html[data-theme=peace] .wisdom', css)
        self.assertIn('html[data-theme=peace] .guidance', css)
        self.assertIn('html[data-theme=peace] .badge', css)
        self.assertIn('.report-highlight', css)
        self.assertIn('.pattern-row', css)
        self.assertIn('.suggestion', css)

if __name__ == '__main__':
    unittest.main()



