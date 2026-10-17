from database.connection import get_db, get_mongo_db, USE_MONGO

def create(user_id,title,body,mood,score,now):
    if USE_MONGO:
        import uuid; doc={'id':str(uuid.uuid4()),'user_id':str(user_id),'title':title,'body':body,'mood':mood,'score':score,'created_at':now,'updated_at':now}; get_mongo_db().journals.insert_one(doc); return doc['id']
    con=get_db(); cur=con.execute('INSERT INTO journals(user_id,title,body,mood,score,created_at,updated_at) VALUES(?,?,?,?,?,?,?)',(user_id,title,body,mood,score,now,now)); con.commit(); uid=cur.lastrowid; con.close(); return uid

def all_for_user(user_id):
    if USE_MONGO: return list(get_mongo_db().journals.find({'user_id':str(user_id)}, {'_id':0}).sort('created_at',-1))
    con=get_db(); rows=con.execute('SELECT * FROM journals WHERE user_id=? ORDER BY created_at DESC',(user_id,)).fetchall(); con.close(); return rows

def find(journal_id,user_id):
    if USE_MONGO: return get_mongo_db().journals.find_one({'id':str(journal_id),'user_id':str(user_id)}, {'_id':0})
    con=get_db(); row=con.execute('SELECT * FROM journals WHERE id=? AND user_id=?',(journal_id,user_id)).fetchone(); con.close(); return row

def update(journal_id,user_id,title,body,mood,score,now):
    if USE_MONGO: get_mongo_db().journals.update_one({'id':str(journal_id),'user_id':str(user_id)},{'$set':{'title':title,'body':body,'mood':mood,'score':score,'updated_at':now}}); return
    con=get_db(); con.execute('UPDATE journals SET title=?,body=?,mood=?,score=?,updated_at=? WHERE id=? AND user_id=?',(title,body,mood,score,now,journal_id,user_id)); con.commit(); con.close()

def delete(journal_id,user_id):
    if USE_MONGO: get_mongo_db().journals.delete_one({'id':str(journal_id),'user_id':str(user_id)}); return
    con=get_db(); con.execute('DELETE FROM journals WHERE id=? AND user_id=?',(journal_id,user_id)); con.commit(); con.close()
