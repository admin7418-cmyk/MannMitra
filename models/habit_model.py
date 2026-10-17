from database.connection import get_db, get_mongo_db, USE_MONGO
from datetime import date, timedelta

def add(user_id, name, today_date):
    if USE_MONGO:
        import uuid
        get_mongo_db().habits.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': str(user_id),
            'name': name,
            'completed': 0,
            'streak': 0,
            'date': today_date
        })
        return
    con = get_db()
    con.execute('INSERT INTO habits(user_id,name,completed,streak,date) VALUES(?,?,0,0,?)',
                (user_id, name, today_date))
    con.commit()
    con.close()

def all_for_user(user_id):
    if USE_MONGO:
        return list(get_mongo_db().habits.find({'user_id': str(user_id)}, {'_id': 0}).sort('date', -1))
    con = get_db()
    rows = con.execute('SELECT * FROM habits WHERE user_id=? ORDER BY id DESC', (user_id,)).fetchall()
    con.close()
    return [dict(r) for r in rows]

create = add


def toggle(habit_id, user_id):
    if USE_MONGO:
        c = get_mongo_db().habits.find_one({'id': str(habit_id), 'user_id': str(user_id)})
        if c:
            new_val = 0 if c.get('completed') else 1
            cur_streak = int(c.get('streak', 0))
            new_streak = cur_streak + 1 if new_val == 1 else max(0, cur_streak - 1)
            get_mongo_db().habits.update_one(
                {'id': str(habit_id), 'user_id': str(user_id)},
                {'$set': {'completed': new_val, 'streak': new_streak}}
            )
        return
    con = get_db()
    row = con.execute('SELECT completed, streak FROM habits WHERE id=? AND user_id=?', (habit_id, user_id)).fetchone()
    if row:
        new_val = 0 if row['completed'] else 1
        new_streak = row['streak'] + 1 if new_val == 1 else max(0, row['streak'] - 1)
        con.execute('UPDATE habits SET completed=?, streak=? WHERE id=? AND user_id=?',
                    (new_val, new_streak, habit_id, user_id))
        con.commit()
    con.close()

def delete(habit_id, user_id):
    if USE_MONGO:
        get_mongo_db().habits.delete_one({'id': str(habit_id), 'user_id': str(user_id)})
        return
    con = get_db()
    con.execute('DELETE FROM habits WHERE id=? AND user_id=?', (habit_id, user_id))
    con.commit()
    con.close()

delete_habit = delete


def get_badges(journals_count=0, completed_habits=0, streak=0):
    """Calculates gamification achievements according to the project proposal."""
    badges = [
        {
            "id": "first_reflection",
            "title": "First Reflection",
            "icon": "🌱",
            "desc": "Wrote your first personal reflection",
            "unlocked": journals_count >= 1
        },
        {
            "id": "mindful_starter",
            "title": "Mindful Starter",
            "icon": "✨",
            "desc": "Completed your first daily wellness habit",
            "unlocked": completed_habits >= 1
        },
        {
            "id": "streak_3",
            "title": "Consistency Flame",
            "icon": "🔥",
            "desc": "Maintained a 3-day reflection streak",
            "unlocked": streak >= 3
        },
        {
            "id": "habit_champ",
            "title": "Habit Champion",
            "icon": "⚡",
            "desc": "Completed 5 wellness habits",
            "unlocked": completed_habits >= 5
        },
        {
            "id": "wisdom_seeker",
            "title": "Gita Seeker",
            "icon": "🪶",
            "desc": "Engaged in reflection and explored Gita wisdom",
            "unlocked": journals_count >= 3
        },
        {
            "id": "streak_7",
            "title": "Zen Master",
            "icon": "🏆",
            "desc": "Achieved a full 7-day wellness streak",
            "unlocked": streak >= 7
        }
    ]
    return badges

