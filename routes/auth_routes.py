from database.models import db, UserTable
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    print(request.method)
    if request.method == "POST":
        email = request.form.get("email")
        user = db.session.execute(db.select(UserTable).where(UserTable.email == email)).scalar_one_or_none()
        if user: # checks if the user already has signed up in with this email
            flash("You've already signed up with that email, log in instead.")
            return redirect(url_for("auth.login"))

        password = request.form.get("password")
        hashed_password = generate_password_hash(password=password, method="pbkdf2:sha256", salt_length=8)

        new_user = UserTable(
            email=email,
            password=hashed_password,
            name=request.form.get("name")
        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home.home"))
    else:
        print(request.method)
    return render_template("register.html", logged_in=current_user.is_authenticated)

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            user = db.session.execute(
                db.select(UserTable).filter_by(email=email)
            ).scalar_one_or_none()
        except SQLAlchemyError:
            current_app.logger.exception("DB error during login")
            flash("Invalid credentials. Please try again.", "error")
            return render_template("login.html")

        if user and check_password_hash(user.password, password):
            login_user(user)
            # flash("Successfully logged in.", "success")
            return redirect(url_for("home.home"))

        flash("Invalid credentials. Try again.", "error")

    return render_template("login.html", logged_in=current_user.is_authenticated)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

