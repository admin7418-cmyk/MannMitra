from flask import Blueprint, render_template, session, redirect, url_for

calm_bp = Blueprint('calm', __name__)

@calm_bp.route('/calm')
def calm_page():
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('auth.login_page'))
    return render_template('calm/calm.html')
