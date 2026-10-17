"""
MannMitra - SQLite to MongoDB Migration Script
Migrates users, journals, chats, habits, and community posts from mannmitra.db to MongoDB.
Run this after setting MONGO_URI in your .env file:
    python database/migrate_to_mongo.py
"""
import os, sqlite3, json
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_FILE = BASE_DIR / "mannmitra.db"
MONGO_URI = os.getenv("MONGO_URI", "").strip()
DB_NAME = os.getenv("DB_NAME", "mannmitra")

def migrate():
    if not MONGO_URI:
        print("[!] ERROR: MONGO_URI is not set in your .env file.")
        print("Please add your MongoDB connection string to .env and run this script again.")
        return

    print(f"Connecting to MongoDB database '{DB_NAME}'...")
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        mongo_db = client[DB_NAME]
        print("[+] MongoDB connection successful!")
    except Exception as e:
        print(f"[!] Could not connect to MongoDB: {e}")
        return

    if not DB_FILE.exists():
        print(f"[!] SQLite file {DB_FILE} not found. Nothing to migrate.")
        return

    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row

    # 1. Users
    try:
        users = con.execute("SELECT * FROM users").fetchall()
        for u in users:
            d = dict(u)
            uid = str(d['id'])
            mongo_db.users.update_one(
                {"email": d['email']},
                {"$set": {
                    "id": uid,
                    "name": d['name'],
                    "email": d['email'],
                    "password": d['password'],
                    "role": d.get('role', 'user'),
                    "preferences": json.loads(d.get('preferences') or '{"language":"en"}'),
                    "created_at": d['created_at']
                }},
                upsert=True
            )
        print(f"[+] Migrated {len(users)} users.")
    except Exception as e:
        print(f"[-] Users migration notice: {e}")

    # 2. Journals
    try:
        journals = con.execute("SELECT * FROM journals").fetchall()
        for j in journals:
            d = dict(j)
            jid = str(d['id'])
            mongo_db.journals.update_one(
                {"id": jid},
                {"$set": {
                    "id": jid,
                    "user_id": str(d['user_id']),
                    "title": d['title'],
                    "body": d['body'],
                    "mood": d['mood'],
                    "score": float(d['score']),
                    "created_at": d['created_at'],
                    "updated_at": d.get('updated_at', d['created_at'])
                }},
                upsert=True
            )
        print(f"[+] Migrated {len(journals)} journals.")
    except Exception as e:
        print(f"[-] Journals migration notice: {e}")

    # 3. Chats
    try:
        chats = con.execute("SELECT * FROM chats").fetchall()
        for c in chats:
            d = dict(c)
            mongo_db.chats.insert_one({
                "user_id": str(d['user_id']),
                "message": d['message'],
                "reply": d['reply'],
                "created_at": d['created_at'],
                "kind": d.get('kind', 'friendly'),
                "gita_reference": d.get('gita_reference', ''),
                "language": d.get('language', 'en')
            })
        print(f"[+] Migrated {len(chats)} chat entries.")
    except Exception as e:
        print(f"[-] Chats migration notice: {e}")

    # 4. Habits
    try:
        habits = con.execute("SELECT * FROM habits").fetchall()
        for h in habits:
            d = dict(h)
            mongo_db.habits.update_one(
                {"id": str(d['id'])},
                {"$set": {
                    "id": str(d['id']),
                    "user_id": str(d['user_id']),
                    "name": d['name'],
                    "completed": int(d.get('completed', 0)),
                    "streak": int(d.get('streak', 0)),
                    "date": d['date']
                }},
                upsert=True
            )
        print(f"[+] Migrated {len(habits)} habits.")
    except Exception as e:
        print(f"[-] Habits migration notice: {e}")

    # 5. Community Posts
    try:
        posts = con.execute("SELECT * FROM community_posts").fetchall()
        for p in posts:
            d = dict(p)
            mongo_db.community_posts.update_one(
                {"id": str(d['id'])},
                {"$set": {
                    "id": str(d['id']),
                    "user_id": str(d.get('user_id') or ''),
                    "message": d['message'],
                    "likes": int(d.get('likes', 0)),
                    "reported": int(d.get('reported', 0)),
                    "created_at": d['created_at']
                }},
                upsert=True
            )
        print(f"[+] Migrated {len(posts)} community posts.")
    except Exception as e:
        print(f"[-] Community migration notice: {e}")

    con.close()
    print("[✓] Migration to MongoDB complete!")

if __name__ == "__main__":
    migrate()
