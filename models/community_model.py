from database.connection import get_db, get_mongo_db, USE_MONGO

def create(user_id, message, created_at):
    if USE_MONGO:
        import uuid
        get_mongo_db().community_posts.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': str(user_id) if user_id else '',
            'message': message,
            'likes': 0,
            'reported': 0,
            'created_at': created_at
        })
        return
    con = get_db()
    con.execute('INSERT INTO community_posts(user_id,message,likes,reported,created_at) VALUES(?,?,0,0,?)',
                (user_id, message, created_at))
    con.commit()
    con.close()

def recent(limit=50, sort_by='recent'):
    if USE_MONGO:
        sort_field = 'likes' if sort_by == 'popular' else 'created_at'
        return list(get_mongo_db().community_posts.find({'reported': {'$lt': 3}}, {'_id':0}).sort(sort_field, -1).limit(limit))
    con = get_db()
    order = 'likes DESC, created_at DESC' if sort_by == 'popular' else 'created_at DESC'
    rows = con.execute(f'SELECT * FROM community_posts WHERE reported < 3 ORDER BY {order} LIMIT ?', (limit,)).fetchall()
    con.close()
    return [dict(r) for r in rows]

def like_post(post_id):
    if USE_MONGO:
        get_mongo_db().community_posts.update_one({'id': str(post_id)}, {'$inc': {'likes': 1}})
        return
    con = get_db()
    con.execute('UPDATE community_posts SET likes = likes + 1 WHERE id = ?', (post_id,))
    con.commit()
    con.close()

def report_post(post_id):
    if USE_MONGO:
        get_mongo_db().community_posts.update_one({'id': str(post_id)}, {'$inc': {'reported': 1}})
        return
    con = get_db()
    con.execute('UPDATE community_posts SET reported = reported + 1 WHERE id = ?', (post_id,))
    con.commit()
    con.close()

def delete_post(post_id):
    if USE_MONGO:
        get_mongo_db().community_posts.delete_one({'id': str(post_id)})
        return
    con = get_db()
    con.execute('DELETE FROM community_posts WHERE id = ?', (post_id,))
    con.commit()
    con.close()

def get_reported():
    if USE_MONGO:
        return list(get_mongo_db().community_posts.find({'reported': {'$gt': 0}}, {'_id':0}).sort('reported', -1))
    con = get_db()
    rows = con.execute('SELECT * FROM community_posts WHERE reported > 0 ORDER BY reported DESC').fetchall()
    con.close()
    return [dict(r) for r in rows]

def count_all():
    if USE_MONGO:
        return get_mongo_db().community_posts.count_documents({})
    con = get_db()
    c = con.execute('SELECT COUNT(*) FROM community_posts').fetchone()[0]
    con.close()
    return c

