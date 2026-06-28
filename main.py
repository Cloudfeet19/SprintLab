# Sprint Lab - Track and Field Sport Analysis

import pandas as pd

from dotenv import load_dotenv
from os import environ

from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import select

from flask_login import login_user, logout_user, LoginManager, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from database.models import db, ResultTable, AthleteTable, UserTable
from helpers.helpers import get_result_data, create_new_athlete, result_in_seconds, results_in_inches, result_in_meters, get_best_results, get_chart_html

from forms.forms import ResultForm, AthleteForm, ALL_EVENTS, FIELD_EVENTS

from src.cleaning import clean_data
from src.features import add_features, get_season, classify_event
from src.analytics import athletes_summary, get_coaches_complete_event_summary
from src.charts import athlete_event_result_chart, athlete_medal_count_chart, current_pr_progression_chart
from src.charts import event_medal_count_chart, ranked_event_bar_chart

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = environ["SECRET_KEY"]
# No users -- Testing
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///SprintLab.db"

# Users - Testing
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///SprintLabPt2.db"

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    db.create_all()

def initialize_dataset(db):
    """
    Convert a sqlalchemy database table to pandas dataframe
    """
    # Gets all results for each athlete in the database
    rows = db.session.execute(
        select(AthleteTable, ResultTable)
        .join(ResultTable, AthleteTable.id == ResultTable.athlete_id)
    ).all()

    data = []

    for athlete, result in rows:
        data.append({
            "athlete_id": athlete.id,
            "name": athlete.name,
            "gender": athlete.gender,
            "grade": result.grade,
            "athlete_class": athlete.athlete_class,
            "event": result.event,
            "raw_result": result.raw_result,
            "result_in_seconds": result.result_in_seconds,
            "result_in_inches": result.result_in_inches,
            "result_in_meters": result.result_in_meters,
            "wind": result.wind,
            "placement": result.placement,
            "date": result.date,
            "meet": result.meet,
            "atmosphere": result.atmosphere,
            "race_type": result.race_type,
            "season": result.season,
            "performance_type": result.performance_type,
        })

    df = pd.DataFrame(data)

    if data: # only clean and add features to the dataframe if there is data

        # Clean Data
        df = clean_data(df)

        # Add features
        df = add_features(df)

    return df

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(UserTable, int(user_id))

@app.route('/register', methods=["GET", "POST"])
def register():
    print(request.method)
    if request.method == "POST":
        email = request.form.get("email")
        user = db.session.execute(db.select(UserTable).where(UserTable.email == email)).scalar_one_or_none()
        if user: # checks if the user already has signed up in with this email
            flash("You've already signed up with that email, log in instead.")
            return redirect(url_for("login"))

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
        return redirect(url_for("home"))
    else:
        print(request.method)
    return render_template("register.html", logged_in=current_user.is_authenticated)

@app.route('/login', methods=["GET", "POST"])
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
            return redirect(url_for("home"))

        flash("Invalid credentials. Try again.", "error")

    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/home")
@login_required
def home():
    return render_template("index.html")

# Complete -- May need upgrading
@app.route("/add-result", methods=["GET", "POST"])
@login_required
def add_result():
    result_form = ResultForm()
    athlete_form = AthleteForm()

    athletes = db.session.execute(
        select(AthleteTable).where(AthleteTable.user_id == current_user.id)
    ).scalars().all()

    selected_athlete_id = request.form.get("athlete_id")

    if request.method == "POST":
        if selected_athlete_id == "new":
            valid = athlete_form.validate() and result_form.validate()
        else:
            valid = result_form.validate()

        if valid:
            if selected_athlete_id == "new":
                athlete = create_new_athlete(athlete_form, current_user)
            else:
                athlete = db.session.get(
                    AthleteTable, selected_athlete_id
                )

            result = get_result_data(result_form, athlete, current_user)

            db.session.add(result)
            db.session.commit()

        return redirect(url_for("add_result"))

    return render_template("add_result.html", result_form=result_form, athlete_form=athlete_form, athletes=athletes)

# Complete -- May need upgrading
@app.route("/athletes_dashboard")
@login_required
def athletes_dashboard():
    # Grabs all athletes for the dropdown
    athletes = db.session.execute(
        select(AthleteTable).where(AthleteTable.user_id == current_user.id)
    ).scalars().all()

    selected_athlete_id = request.args.get("athlete_id", type=int)
    selected_athlete = None
    events = []
    selected_event = None

    chart_html = None
    pr_chart_html = None
    medal_count_html = None
    summary = {}
    current_pr = None

    if selected_athlete_id:
        # Gets the selected athlete from the get request / form
        selected_athlete = db.session.get(AthleteTable, selected_athlete_id)

        # Gets the events the selected athlete has results for, uses distinct so that it doesnt grab the event item for every result in the database
        events = db.session.execute(
            select(ResultTable.event)
            .where(ResultTable.athlete_id == selected_athlete_id)
            .distinct()
        ).scalars().all()

        # Gets the selected event from the get request / form, Otherwise no event is selected
        selected_event = request.args.get("event")

        # Ensures to populate the events that are passed to jinja the correct events based on
        # the selected athlete so that the dropbox and display can populate dynamically
        if events and selected_event not in events:
            selected_event = events[0]

        if selected_event:
            # turn the database object into a pandas dataframe so that we can apply the analytics charts and features
            df = initialize_dataset(db)

            df = df[df["event"] == selected_event]

            # grabs all charts and analytics features to pass to the HTML
            chart = athlete_event_result_chart(df, selected_athlete_id, selected_event)
            chart_html = chart.to_html(full_html=False)

            pr_chart = current_pr_progression_chart(df, selected_athlete_id, selected_event)
            pr_chart_html = pr_chart.to_html(full_html=False)

            medal_count = athlete_medal_count_chart(df, selected_athlete_id)
            medal_count_html = medal_count.to_html(full_html=False)

            summary = athletes_summary(df, selected_athlete_id)
            current_pr = summary["current_prs"][selected_event]

    return render_template(
        "athletes_dashboard.html",
        athletes=athletes,
        selected_athlete_id=selected_athlete_id,
        selected_athlete=selected_athlete,
        events=events,
        selected_event=selected_event,
        chart_html=chart_html,
        pr_chart_html=pr_chart_html,
        medal_count_html=medal_count_html,
        summary=summary,
        current_pr=current_pr
    )

@app.route("/event_dashboard")
@login_required
def event_dashboard():
    selected_event = request.args.get("event")
    summary = {}
    all_medal_chart = None
    male_medal_chart = None
    female_medal_chart = None
    male_event_ranking_chart = None
    female_event_ranking_chart = None


    if selected_event:
        # Initialize pandas dataframe from sql database
        df = initialize_dataset(db)

        if not df.empty: # Checks if df is empty
            # grabs the summary to display in the html for the selected event
            summary = get_coaches_complete_event_summary(df, selected_event)

            # the combined medal chart for the selected event, male and female
            all_medal_chart = event_medal_count_chart(df, selected_event)
            all_medal_chart = all_medal_chart.to_html(full_html=False, config={"responsive": True}) if all_medal_chart else None

            # male medal chart only for the selected event
            male_df = df[df["gender"] == "Male"]
            male_medal_chart = event_medal_count_chart(male_df, selected_event)
            male_medal_chart = male_medal_chart.to_html(full_html=False, config={"responsive": True}) if male_medal_chart else None

            # filters and groups the data by event and gender
            event_filtered_male_df = male_df[male_df["event"] == selected_event]
            male_grouped_df = event_filtered_male_df.groupby(["athlete_id"], as_index=False, observed=True)

            # gets the best result from each group of data passed in
            male_best_results = get_best_results(male_grouped_df)

            # sorts the data / flips the chart if it is a field event
            if male_best_results:
                male_sorted_best_result_data = sorted(male_best_results, key=lambda result_data: result_data["best_result"])
                if selected_event in FIELD_EVENTS:
                    male_sorted_best_result_data = sorted(male_best_results, key=lambda result_data: result_data["best_result"], reverse=True)


                # charts the data and prepares it to be sent to the HTML file
                male_event_ranking_chart = ranked_event_bar_chart(male_sorted_best_result_data, selected_event)
                male_event_ranking_chart = male_event_ranking_chart.to_html(full_html=False,
                                                            config={"responsive": True}) if male_event_ranking_chart else None

            ####################################################
            # female medal chart for the selected event
            female_df = df[df["gender"] == "Female"]
            female_medal_chart = event_medal_count_chart(female_df, selected_event)
            female_medal_chart = female_medal_chart.to_html(full_html=False, config={"responsive": True}) if female_medal_chart else None

            # filters and groups the data by event and gender
            event_filtered_female_df = female_df[female_df["event"] == selected_event]
            female_grouped_df = event_filtered_female_df.groupby(["athlete_id"], as_index=False, observed=True)

            # gets the best result from each group of data passed in
            female_best_results = get_best_results(female_grouped_df)

            female_sorted_best_result_data = None

            # sorts the data / flips the chart if it is a field event
            if female_best_results:
                female_sorted_best_result_data = sorted(female_best_results, key=lambda result_data: result_data["best_result"])
                if selected_event in FIELD_EVENTS:
                    female_sorted_best_result_data = sorted(female_best_results, key=lambda result_data: result_data["best_result"], reverse=True)

                # charts the data and prepares it to be sent to the HTML file
                female_event_ranking_chart = ranked_event_bar_chart(female_sorted_best_result_data, selected_event)
                female_event_ranking_chart = female_event_ranking_chart.to_html(full_html=False,
                                                                                config={"responsive": True}) if female_event_ranking_chart else None


    return render_template(
        "event_dashboard.html",
        events=ALL_EVENTS,
        selected_event=selected_event,
        summary=summary,
        all_medal_chart=all_medal_chart,
        male_medal_chart=male_medal_chart,
        female_medal_chart=female_medal_chart,
        male_event_ranking_chart=male_event_ranking_chart,
        female_event_ranking_chart=female_event_ranking_chart
    )

@app.route("/compare")
@login_required
def compare():
    athletes = db.session.execute(
        select(AthleteTable).where(AthleteTable.user_id == current_user.id)
    ).scalars().all()
    events = ALL_EVENTS
    selected_event = request.args.get("event")
    athlete_one_id = request.args.get("athlete_one_id")
    athlete_two_id = request.args.get("athlete_two_id")

    athlete_one = db.session.get(AthleteTable, athlete_one_id)
    athlete_two = db.session.get(AthleteTable, athlete_two_id)

    # initialize potentially empty objects
    athlete_one_summary = None
    athlete_two_summary = None

    athlete_one_result_chart_html = None
    athlete_two_result_chart_html = None

    athlete_one_pr_chart_html = None
    athlete_two_pr_chart_html = None

    athlete_one_medal_chart_html = None
    athlete_two_medal_chart_html = None

    # initalize the dataframe for later filtering
    if athlete_one and athlete_two and selected_event:
        df = initialize_dataset(db)

    if athlete_one and selected_event:
        # create a df of result for the athlete with the selected event
        df_athlete_one = df[df["athlete_id"] == athlete_one.id]
        df_athlete_one_event = df_athlete_one[df_athlete_one["event"] == selected_event]

        # ensure that to create the summary and chart, there is data for the selected athlete and event
        if not df_athlete_one_event.empty:
            athlete_one_id = int(athlete_one_id)
            athlete_one_summary = athletes_summary(df_athlete_one_event, athlete_one_id)

            athlete_one_result_chart = athlete_event_result_chart(df, athlete_one_id, selected_event)
            athlete_one_result_chart_html = get_chart_html(athlete_one_result_chart)

            athlete_one_pr_chart = current_pr_progression_chart(df, athlete_one_id, selected_event)
            athlete_one_pr_chart_html = get_chart_html(athlete_one_pr_chart)

            athlete_one_medal_chart = athlete_medal_count_chart(df, athlete_one_id)
            athlete_one_medal_chart_html = get_chart_html(athlete_one_medal_chart)

    if athlete_two and selected_event:
        # create a dataframe of result for the athlete with the selected event
        df_athlete_two = df[df["athlete_id"] == athlete_two.id]
        df_athlete_two_event = df_athlete_two[df_athlete_two["event"] == selected_event]

        # ensure that to create the summary and chart, there is data for the selected athlete and event
        if not df_athlete_two_event.empty:
            athlete_two_id = int(athlete_two_id)
            athlete_two_summary = athletes_summary(df_athlete_two_event, athlete_two_id)

            athlete_two_result_chart = athlete_event_result_chart(df, athlete_two_id, selected_event)
            athlete_two_result_chart_html = get_chart_html(athlete_two_result_chart)

            athlete_two_pr_chart = current_pr_progression_chart(df, athlete_two_id, selected_event)
            athlete_two_pr_chart_html = get_chart_html(athlete_two_pr_chart)

            athlete_two_medal_chart = athlete_medal_count_chart(df, athlete_two_id)
            athlete_two_medal_chart_html = get_chart_html(athlete_two_medal_chart)

    return render_template("compare.html",
                           athletes=athletes,
                           events=events,
                           selected_event=selected_event,
                           athlete_one_id=athlete_one_id,
                           athlete_two_id=athlete_two_id,
                           athlete_one=athlete_one,
                           athlete_two=athlete_two,
                           athlete_one_summary=athlete_one_summary,
                           athlete_two_summary=athlete_two_summary,
                           athlete_one_result_chart=athlete_one_result_chart_html,
                           athlete_two_result_chart=athlete_two_result_chart_html,
                           athlete_one_pr_chart=athlete_one_pr_chart_html,
                           athlete_two_pr_chart=athlete_two_pr_chart_html,
                           athlete_one_medal_chart=athlete_one_medal_chart_html,
                           athlete_two_medal_chart=athlete_two_medal_chart_html
                           )

if __name__ == '__main__':
    app.run(debug=True, port=5050)







