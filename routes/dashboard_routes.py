from datetime import datetime, timedelta
from flask import Blueprint, render_template, session, redirect, url_for
from models.user_model import find_by_id
from models.journal_model import all_for_user
from models.habit_model import all_for_user as all_habits
from models.chat_model import recent
from services.report_service import build_summary
from services.gita_service import recommend
from services.ai_service import build_profile, personalized_insight

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard_page():
    uid=session.get('user_id')
    if not uid:return redirect(url_for('auth.login_page'))
    user=find_by_id(uid); journals=all_for_user(uid); habits=all_habits(uid); chats=recent(uid,20)
    summary=build_summary(journals); profile=build_profile(journals,chats)
    moods=[{'date':r['created_at'][:10],'score':r['score']} for r in journals[:14][::-1]]
    dates={r['created_at'][:10] for r in journals}; day=datetime.now().date(); streak=0
    while day.isoformat() in dates: streak+=1; day-=timedelta(days=1)
    week_ago=(datetime.now()-timedelta(days=7)).isoformat(); weekly=[r for r in journals if r['created_at']>=week_ago]
    weekly_avg=round(sum(float(r['score']) for r in weekly)/len(weekly),2) if weekly else 0
    latest=journals[0] if journals else None
    wisdom=recommend(latest['body'] if latest else 'stress focus peace')
    insight=personalized_insight(profile)
    return render_template('dashboard/dashboard.html',user=user,journals=journals,summary=summary,moods=moods,streak=streak,weekly_count=len(weekly),weekly_avg=weekly_avg,completed_habits=sum(r['completed'] for r in habits),total_habits=len(habits),latest=latest,wisdom=wisdom,ai_profile=profile,ai_insight=insight)
