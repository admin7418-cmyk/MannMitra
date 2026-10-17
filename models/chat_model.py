from database.connection import get_db, get_mongo_db, USE_MONGO

def save(user_id, message, reply, created_at, kind='friendly', gita_reference='', language='en'):
    if USE_MONGO:
        get_mongo_db().chats.insert_one({
            'user_id': str(user_id),
            'message': message,
            'reply': reply,
            'created_at': created_at,
            'kind': kind,
            'gita_reference': gita_reference or '',
            'language': language or 'en'
        })
        return
    con=get_db()
    con.execute('INSERT INTO chats(user_id,message,reply,created_at,kind,gita_reference,language) VALUES(?,?,?,?,?,?,?)',
                (user_id, message, reply, created_at, kind, gita_reference or '', language or 'en'))
    con.commit()
    con.close()

def recent(user_id, limit=30):
    if USE_MONGO:
        return list(get_mongo_db().chats.find({'user_id':str(user_id)}, {'_id':0}).sort('created_at',-1).limit(limit))
    con=get_db()
    rows=con.execute('SELECT * FROM chats WHERE user_id=? ORDER BY created_at DESC LIMIT ?',(user_id,limit)).fetchall()
    con.close()
    return rows

def count_all():
    if USE_MONGO:
        return get_mongo_db().chats.count_documents({})
    con=get_db()
    c=con.execute('SELECT COUNT(*) FROM chats').fetchone()[0]
    con.close()
    return c

def clear_for_user(user_id):
    if USE_MONGO:
        get_mongo_db().chats.delete_many({'user_id': str(user_id)})
        return
    con = get_db()
    con.execute('DELETE FROM chats WHERE user_id = ?', (user_id,))
    con.commit()
    con.close()


