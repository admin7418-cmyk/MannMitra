from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import find_by_id, find_by_identifier, all_users
from models.community_model import recent as all_posts, delete_post, get_reported, count_all as count_posts
from models.chat_model import count_all as count_chats
from database.connection import get_db_status, get_db, get_mongo_db, check_mongo_available
from services.auth_service import authenticate

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        username = (request.form.get('username') or request.form.get('email') or '').strip()
        password = request.form.get('password', '').strip()

        # Check required credentials: username 'admin' and password 'Admin@118119'
        if username.lower() == 'admin' and password == 'Admin@118119':
            session['admin_logged_in'] = True
            session['admin_username'] = 'admin'
            session.permanent = True
            admin_user = find_by_identifier('admin')
            if admin_user:
                session['admin_id'] = admin_user.get('id')
                if not session.get('user_id'):
                    session['user_id'] = admin_user.get('id')
                    session['user_name'] = admin_user.get('name')
                    session['role'] = 'admin'
            flash('Admin authentication successful. Welcome to Admin Control Center.', 'success')
            return redirect(url_for('admin.admin_dashboard'))

        # Fallback to database authentication if user exists with role == 'admin'
        user = authenticate(username, password)
        if user and user.get('role') == 'admin':
            session['admin_logged_in'] = True
            session['admin_username'] = user.get('name')
            session['admin_id'] = user.get('id')
            session.permanent = True
            if not session.get('user_id'):
                session['user_id'] = user.get('id')
                session['user_name'] = user.get('name')
                session['role'] = 'admin'
            flash('Admin authentication successful. Welcome to Admin Control Center.', 'success')
            return redirect(url_for('admin.admin_dashboard'))

        flash('Invalid Admin credentials. Access denied. (Only admin / Admin@118119 is permitted)', 'error')

    return render_template('admin/admin_login.html')

@admin_bp.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    session.pop('admin_id', None)
    flash('Administrator session safely terminated.', 'info')
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('')
@admin_bp.route('/')
def admin_dashboard():
    # Strict role protection: regular users cannot access admin portal
    if not session.get('admin_logged_in'):
        flash('Access restricted to Administrators. Please log in with admin credentials.', 'error')
        return redirect(url_for('admin.admin_login'))

    user = None
    admin_id = session.get('admin_id') or session.get('user_id')
    if admin_id:
        user = find_by_id(admin_id)

    db_status = get_db_status()
    users = all_users(30)
    reported = get_reported()
    posts = all_posts(30)

    # Calculate counts
    total_users = len(users)
    total_posts = count_posts()
    total_chats = count_chats()

    # Get journals count
    total_journals = 0
    if check_mongo_available():
        total_journals = get_mongo_db().journals.count_documents({})
    else:
        con = get_db()
        total_journals = con.execute('SELECT COUNT(*) FROM journals').fetchone()[0]
        con.close()

    return render_template('admin/admin.html',
                           user=user,
                           db_status=db_status,
                           users=users,
                           reported=reported,
                           posts=posts,
                           total_users=total_users,
                           total_posts=total_posts,
                           total_chats=total_chats,
                           total_journals=total_journals)

@admin_bp.post('/delete-post/<post_id>')
def admin_delete_post(post_id):
    if not session.get('admin_logged_in'):
        flash('Unauthorized action.', 'error')
        return redirect(url_for('admin.admin_login'))
    delete_post(post_id)
    flash('Community post deleted by Administrator.', 'success')
    return redirect(url_for('admin.admin_dashboard'))
