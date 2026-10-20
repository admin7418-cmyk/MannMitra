import os, sqlite3, logging
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_FILE = BASE_DIR / 'mannmitra.db'
_mongo_client = None
_mongo_db = None
_mongo_checked = False
_mongo_available = False

def check_mongo_available():
    global _mongo_client, _mongo_db, _mongo_checked, _mongo_available
    if _mongo_checked:
        return _mongo_available
    _mongo_checked = True
    uri = os.getenv('MONGO_URI', '').strip()
    if not uri:
        _mongo_available = False
        return False
    try:
        from pymongo import MongoClient
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        _mongo_client = client
        _mongo_db = _mongo_client[os.getenv('DB_NAME', 'mannmitra')]
        _mongo_available = True
        print(f"[MannMitra] Connected successfully to MongoDB: {os.getenv('DB_NAME', 'mannmitra')}")
        return True
    except Exception as e:
        _mongo_available = False
        print(f"[MannMitra] MongoDB URI configured but unreachable ({e}). Falling back to local SQLite database.")
        return False

# Proxy property for backwards compatibility
class _MongoFlagProxy:
    def __bool__(self):
        return check_mongo_available()

USE_MONGO = _MongoFlagProxy()

def get_db():
    if check_mongo_available():
        raise RuntimeError('Mongo mode is enabled. Use get_mongo_db().')
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    return con

def get_mongo_db():
    if not check_mongo_available():
        return None
    return _mongo_db

def get_db_status():
    uri = os.getenv('MONGO_URI', '').strip()
    is_mongo = check_mongo_available()
    if is_mongo:
        engine_type = "MongoDB Atlas" if "mongodb+srv" in uri else "MongoDB Local"
        return {
            "engine": engine_type,
            "connected": True,
            "uri_configured": True,
            "db_name": os.getenv('DB_NAME', 'mannmitra'),
            "mode": "mongo"
        }
    return {
        "engine": "SQLite (mannmitra.db)",
        "connected": True,
        "uri_configured": bool(uri),
        "db_name": "mannmitra.db",
        "mode": "sqlite"
    }

def init_database():
    if check_mongo_available():
        try:
            db = get_mongo_db()
            for name in ['users', 'journals', 'chats', 'habits', 'community_posts']:
                db[name].create_index('user_id')
            db['users'].create_index('email', unique=True)
            db['journals'].create_index([('user_id', 1), ('created_at', -1)])
            db['chats'].create_index([('user_id', 1), ('created_at', -1)])
            db['community_posts'].create_index([('created_at', -1)])
            seed_admin_user()
            return
        except Exception as e:
            print(f"[MannMitra] Error initializing MongoDB indexes: {e}")

    # SQLite fallback / default initialization
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    con.executescript('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        preferences TEXT DEFAULT '{"language": "en"}',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS journals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        mood TEXT NOT NULL,
        score REAL NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        reply TEXT NOT NULL,
        created_at TEXT NOT NULL,
        kind TEXT DEFAULT 'friendly',
        gita_reference TEXT DEFAULT '',
        language TEXT DEFAULT 'en'
    );
    CREATE TABLE IF NOT EXISTS habits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        date TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS community_posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT NOT NULL,
        likes INTEGER DEFAULT 0,
        reported INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS user_memory(
        user_id TEXT PRIMARY KEY,
        name TEXT DEFAULT '',
        career_interest TEXT DEFAULT '',
        primary_goal TEXT DEFAULT '',
        known_concerns TEXT DEFAULT '[]',
        preferences TEXT DEFAULT '{}',
        last_discussed_topic TEXT DEFAULT '',
        interaction_count INTEGER DEFAULT 0,
        positive_feedback_count INTEGER DEFAULT 0,
        negative_feedback_count INTEGER DEFAULT 0,
        updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS response_feedback(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        response_id TEXT,
        category TEXT,
        intent TEXT,
        theme_id TEXT,
        rating INTEGER NOT NULL,
        comment TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );
    ''')
    # Safe migrations for existing SQLite databases
    migrations = [
        "ALTER TABLE chats ADD COLUMN kind TEXT DEFAULT 'friendly'",
        "ALTER TABLE chats ADD COLUMN gita_reference TEXT DEFAULT ''",
        "ALTER TABLE chats ADD COLUMN language TEXT DEFAULT 'en'",
        "ALTER TABLE habits ADD COLUMN streak INTEGER DEFAULT 0",
        "ALTER TABLE community_posts ADD COLUMN likes INTEGER DEFAULT 0",
        "ALTER TABLE community_posts ADD COLUMN reported INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN preferences TEXT DEFAULT '{\"language\": \"en\"}'"
    ]
    for sql in migrations:
        try:
            con.execute(sql)
        except sqlite3.OperationalError:
            pass
    con.commit()
    con.close()
    seed_admin_user()

def seed_admin_user():
    from werkzeug.security import generate_password_hash
    admin_pass = "Admin@118119"
    admin_hash = generate_password_hash(admin_pass)
    now = "2026-09-30T00:00:00"

    if check_mongo_available():
        try:
            db = get_mongo_db()
            existing = db.users.find_one({'$or': [{'email': 'admin'}, {'name': 'admin'}]})
            if not existing:
                db.users.insert_one({
                    'id': 'admin_master',
                    'name': 'admin',
                    'email': 'admin',
                    'password': admin_hash,
                    'role': 'admin',
                    'preferences': {'language': 'en'},
                    'created_at': now
                })
            else:
                update_fields = {'password': admin_hash, 'role': 'admin'}
                if not existing.get('id'):
                    update_fields['id'] = 'admin_master'
                db.users.update_one({'_id': existing['_id']}, {'$set': update_fields})
        except Exception as e:
            print(f"[MannMitra] Error seeding admin in Mongo: {e}")
    else:
        try:
            con = sqlite3.connect(DB_FILE)
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT id FROM users WHERE LOWER(email)='admin' OR LOWER(name)='admin'").fetchone()
            if not row:
                con.execute(
                    "INSERT INTO users(name,email,password,role,preferences,created_at) VALUES(?,?,?,?,?,?)",
                    ('admin', 'admin', admin_hash, 'admin', '{"language": "en"}', now)
                )
            else:
                con.execute("UPDATE users SET password=?, role='admin' WHERE id=?", (admin_hash, row['id']))
            con.commit()
            con.close()
        except Exception as e:
            print(f"[MannMitra] Error seeding admin in SQLite: {e}")


