from flask import Flask
from config import Config
from database.connection import init_database
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.journal_routes import journal_bp
from routes.chat_routes import chat_bp
from routes.gita_routes import gita_bp
from routes.habit_routes import habit_bp
from routes.community_routes import community_bp
from routes.api_routes import api_bp
from routes.home_routes import home_bp
from routes.insights_routes import insights_bp
from routes.report_routes import report_bp
from routes.calm_routes import calm_bp
from routes.profile_routes import profile_bp
from routes.admin_routes import admin_bp
from routes.chatbot_routes import chatbot_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_database()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(gita_bp)
    app.register_blueprint(habit_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(calm_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
