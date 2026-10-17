from flask import Blueprint, render_template, request, session, redirect, url_for
from datetime import date
from services.gita_service import search, GITA, get_verse_in_lang

gita_bp = Blueprint("gita", __name__)

@gita_bp.route("/gita")
def gita_page():
    if not session.get("user_id"):
        return redirect(url_for("auth.login_page"))

    q = request.args.get("q", "").strip()
    theme = request.args.get("theme", "all")
    lang = request.args.get("lang", session.get("lang", "en")).lower().strip()
    if lang not in ["en", "hi", "hinglish"]:
        lang = "en"
    session["lang"] = lang

    items = search(q, theme, lang=lang)
    themes = sorted(set(x["theme"] for x in GITA))
    raw_daily = GITA[date.today().toordinal() % len(GITA)] if GITA else None
    daily = get_verse_in_lang(raw_daily, lang=lang) if raw_daily else None

    return render_template(
        "gita/gita.html",
        items=items,
        themes=themes,
        selected=theme,
        q=q,
        daily=daily,
        lang=lang
    )

