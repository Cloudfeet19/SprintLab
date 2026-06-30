from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home.home"))
    return redirect(url_for("auth.login"))

@home_bp.route("/home")
@login_required
def home():
    return render_template("index.html")
