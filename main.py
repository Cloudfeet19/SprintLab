# Sprint Lab - Track and Field Sport Analysis

from dotenv import load_dotenv
from os import environ

from flask import Flask
from flask_login import LoginManager

from database.models import db, UserTable

from routes.auth_routes import auth_bp
from routes.home_routes import home_bp
from routes.app_feature_routes import features_bp
from routes.dashboard_routes import dashboard_bp

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = environ["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///SprintLabPt2.db"

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(UserTable, int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(features_bp)
app.register_blueprint(dashboard_bp)

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, port=5050)








