# Sprint Lab - Track and Field Sport Analysis
from xml.sax.handler import property_interning_dict

import pandas as pd

from dotenv import load_dotenv
from os import environ

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, create_engine

from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from database.models import db, ResultTable, AthleteTable
from database.helpers.athlete_helpers import query_athlete, result_in_seconds, results_in_inches, result_in_meters

from forms.forms import ResultForm

from src.cleaning import clean_data
from src.features import add_features, get_season, classify_event
from src.analytics import athletes_summary, ranking_coached_events
from src.charts import athlete_event_result_chart, coaching_event_rankings_chart, medal_count_chart, current_pr_progression_chart

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = environ["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///SprintLab.db"

db.init_app(app)

with app.app_context():
    db.create_all()

def initialize_dataset(db) -> pd.DataFrame:
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

    # Clean Data
    df = clean_data(df)

    # Add features
    df = add_features(df)

    return df

@app.route("/")
def home():
    return render_template("index.html")

# Complete
@app.route("/add-result", methods=["GET", "POST"])
def add_result():
    form = ResultForm()

    if form.validate_on_submit():
        athlete = query_athlete(form)

        result = ResultTable()
        result.event = form.event.data
        result.athlete = athlete
        result.grade = form.grade.data
        result.raw_result = form.result.data
        result.result_in_seconds = result_in_seconds(form.result.data, classify_event(str(form.event.data)))
        result.result_in_inches = results_in_inches(form.result.data, classify_event(str(form.event.data)))
        if result.result_in_inches:
            result.result_in_meters = result_in_meters(result.result_in_inches)
        else:
            result.result_in_meters = None
        result.wind = form.wind.data
        result.placement = form.placement.data
        result.date = form.date.data
        result.season = get_season(form.date.data, form.atmosphere.data)
        result.meet = form.meet.data
        result.atmosphere = form.atmosphere.data
        result.race_type = form.race_type.data
        result.performance_type = form.performance_type.data


        db.session.add(result)
        db.session.commit()

        return redirect(url_for("add_result"))

    return render_template("add_result.html", form=form)

@app.route("/athletes")
def athletes():
    return render_template("athletes.html")

@app.route("/athletes_dashboard")
def athletes_dashboard():
    # Grabs all athletes for the dropdown
    athletes = db.session.execute(select(AthleteTable)).scalars().all()

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

            # grabs all charts and analytics features to pass to the HTML
            chart = athlete_event_result_chart(df, selected_athlete_id, selected_event)
            chart_html = chart.to_html(full_html=False)

            pr_chart = current_pr_progression_chart(df, selected_athlete_id, selected_event)
            pr_chart_html = pr_chart.to_html(full_html=False)

            medal_count = medal_count_chart(df, selected_athlete_id)
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

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/event_dashboard/<event_name>")
def event_dashboard(event_name):
    return render_template("event_dashboard.html", event_name=event_name)

@app.route("/compare")
def compare():
    return render_template("compare.html")

if __name__ == '__main__':
    app.run(debug=True, port=5050)






