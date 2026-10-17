import json
from database.connection import get_db, get_mongo_db, USE_MONGO

def find_by_email(email):
    email = (email or '').strip()
    if not email: return None
    if USE_MONGO:
        import re
        return get_mongo_db().users.find_one({'email': {'$regex': f'^{re.escape(email)}$', '$options': 'i'}}, {'_id':0})
    con=get_db(); row=con.execute('SELECT * FROM users WHERE LOWER(email)=LOWER(?)',(email,)).fetchone(); con.close()
    return dict(row) if row else None

def find_by_identifier(identifier):
    identifier = (identifier or '').strip()
    if not identifier: return None
    if USE_MONGO:
        import re
        pattern = f'^{re.escape(identifier)}$'
        return get_mongo_db().users.find_one({
            '$or': [
                {'email': {'$regex': pattern, '$options': 'i'}},
                {'name': {'$regex': pattern, '$options': 'i'}}
            ]
        }, {'_id': 0})
    con=get_db()
    row=con.execute('SELECT * FROM users WHERE LOWER(email)=LOWER(?) OR LOWER(name)=LOWER(?)', (identifier, identifier)).fetchone()
    con.close()
    return dict(row) if row else None

def find_by_id(user_id):
    if not user_id: return None
    if USE_MONGO: return get_mongo_db().users.find_one({'id':str(user_id)}, {'_id':0})
    con=get_db(); row=con.execute('SELECT * FROM users WHERE id=?',(user_id,)).fetchone(); con.close()
    return dict(row) if row else None

def create_user(name,email,password_hash,created_at,role='user'):
    if USE_MONGO:
        import uuid
        uid=str(uuid.uuid4())
        get_mongo_db().users.insert_one({
            'id':uid,
            'name':name,
            'email':email,
            'password':password_hash,
            'role':role,
            'preferences':{'language':'en'},
            'created_at':created_at
        })
        return uid
    con=get_db(); cur=con.execute('INSERT INTO users(name,email,password,role,preferences,created_at) VALUES(?,?,?,?,?,?)',(name,email,password_hash,role,'{"language":"en"}',created_at)); con.commit(); uid=cur.lastrowid; con.close(); return uid

def update_profile(user_id, name=None, language='en'):
    if USE_MONGO:
        update_data = {}
        if name: update_data['name'] = name
        update_data['preferences.language'] = language
        get_mongo_db().users.update_one({'id':str(user_id)}, {'$set': update_data})
        return
    con=get_db()
    if name:
        con.execute('UPDATE users SET name=?, preferences=? WHERE id=?',(name, json.dumps({'language': language}), user_id))
    else:
        con.execute('UPDATE users SET preferences=? WHERE id=?',(json.dumps({'language': language}), user_id))
    con.commit(); con.close()

def all_users(limit=50):
    if USE_MONGO:
        return list(get_mongo_db().users.find({}, {'password': 0, '_id': 0}).sort('created_at', -1).limit(limit))
    con=get_db()
    rows=con.execute('SELECT id, name, email, role, preferences, created_at FROM users ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    con.close()
    return [dict(r) for r in rows]

