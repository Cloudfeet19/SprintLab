from database.models import db, AthleteTable, ResultTable
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from forms.forms import ALL_EVENTS, FIELD_EVENTS
from helpers.dataframe_helpers import initialize_dataset
from helpers.helpers import get_chart_html, get_best_results
from sqlalchemy import select
from src.analytics import get_coaches_complete_event_summary, athletes_summary, get_prs, ranking_coached_events
from src.charts import (
    athlete_event_result_chart,
    athlete_medal_count_chart,
    event_medal_count_chart,
    ranked_event_bar_chart,
    current_pr_progression_chart

)

dashboard_bp = Blueprint("dashboard", __name__)

# Complete -- May need upgrading
@dashboard_bp.route("/athletes_dashboard")
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
            df = initialize_dataset(db, current_user.id)

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

@dashboard_bp.route("/event_dashboard")
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
        df = initialize_dataset(db, current_user.id)

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

@dashboard_bp.route("/compare")
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
        df = initialize_dataset(db, current_user.id)

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

