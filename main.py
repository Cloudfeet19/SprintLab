# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

import pandas as pd

from dotenv import load_dotenv
from os import environ

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
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


def initialize_dataset():
    df = pd.read_csv(r"data/SprintLab_Sample_Data.csv")

    # Clean Data
    df = clean_data(df)

    # Add Features
    df = add_features(df)

    return df



df = initialize_dataset()

@app.route("/")
def home():
    return render_template("index.html")


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


@app.route("/athletes/<athlete_name>")
def athlete_dashboard(athlete_name):
    return render_template("athlete_dashboard.html", athlete_name=athlete_name)


@app.route("/events")
def events():
    return render_template("events.html")


@app.route("/events/<event_name>")
def event_dashboard(event_name):
    return render_template("event_dashboard.html", event_name=event_name)


@app.route("/compare")
def compare():
    return render_template("compare.html")

if __name__ == '__main__':
    app.run(debug=True, port=5050)






