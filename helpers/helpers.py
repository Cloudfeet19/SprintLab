import pandas as pd
from database.models import AthleteTable, ResultTable
from forms.forms import TRACK_EVENTS, FIELD_EVENTS
from sqlalchemy import select
from src.features import classify_event, get_season


def get_chart_html(chart):
    """
    Helper function to easily return plotly chart html without code clutter
    """
    chart_html = chart.to_html(full_html=False, config={"responsive": True}) if chart else None
    return chart_html

def create_new_athlete(form, current_user):
    """
    :param form: Results form
    :return: Returns the specified athlete after checking if the athlete already exists in the Database or not
    """
    first_name = form.first_name.data.strip().title()
    last_name = form.last_name.data.strip().title()
    athlete_class = form.athlete_class.data.strip()
    gender = form.gender.data.strip()
    athlete_name = f"{first_name} {last_name}"

    """    # assigns the first iteration of the athlete in the database to the athlete variable
    athlete = AthleteTable.query.filter_by(name=athlete_name, athlete_class=athlete_class, gender=gender).first()

    # if the athlete already exists, return that specific athlete
    if athlete:
        return athlete"""

    # otherwise create the new athlete and return them
    athlete = AthleteTable(
        name = athlete_name,
        gender = form.gender.data,
        athlete_class = form.athlete_class.data,
        user = current_user
    )

    return athlete

def result_in_seconds(result:str, event_type:str) -> float:
    if event_type == "field": return None

    if ":" in result:
        result = result.split(":")
        total_seconds = (float(result[0]) * 60) + float(result[1])
    else:
        total_seconds = float(result)
    return round(total_seconds, 2)

def results_in_inches(result:str, event_type: str) -> float:
    if event_type == "track": return None

    if "-" in result:
        result = result.split("-")
    elif "'" in result:
        result = result.split("'")

    total_inches = (float(result[0]) * 12) + float(result[1])

    return round(total_inches, 2)

def result_in_meters(inches: float) -> float:
    return round(inches * 0.0254, 2)

def get_best_results(groups):
    """
    :param groups: Takes a gender and event filtered set of grouped dataframes
    :return: Returns the data of the best result from each grouped dataframe
    """
    if not groups:
        return None

    best_results = []

    for group in groups:
        dataset = group[1]
        name = dataset["name"].iloc[0]
        if dataset["better_direction"].iloc[0] == "lower":
            best_result_index = (dataset["result_value"] == dataset["result_value"].min()).idxmax()
            best_result_value = dataset.at[best_result_index, "result_value"]
            best_raw_result =   dataset.at[best_result_index, "raw_result"]

        elif dataset["better_direction"].iloc[0] == "higher":
            best_result_index = (dataset["result_value"] == dataset["result_value"].max()).idxmax()
            best_result_value = dataset.at[best_result_index, "result_value"]
            best_raw_result =   dataset.at[best_result_index, "raw_result"]

        else:
            best_result_value = None
            best_raw_result = None

        result_data = {
            "name": name,
            "best_result": best_result_value,
            "best_raw_result": best_raw_result
        }

        best_results.append(result_data)
    return best_results


def get_result_data(result_form, athlete, current_user):
    result = ResultTable()

    result.event = result_form.event.data
    result.athlete_id = athlete.id
    result.user_id = current_user.id
    result.grade = result_form.grade.data
    result.raw_result = result_form.result.data
    result.result_in_seconds = result_in_seconds(result_form.result.data, classify_event(str(result_form.event.data)))
    result.result_in_inches = results_in_inches(result_form.result.data, classify_event(str(result_form.event.data)))
    if result.result_in_inches:
        result.result_in_meters = result_in_meters(result.result_in_inches)
    else:
        result.result_in_meters = None
    result.wind = result_form.wind.data
    result.placement = result_form.placement.data
    result.date = result_form.date.data
    result.season = get_season(result_form.date.data, result_form.atmosphere.data)
    result.meet = result_form.meet.data
    result.atmosphere = result_form.atmosphere.data
    result.race_type = result_form.race_type.data
    result.performance_type = result_form.performance_type.data

    return result


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
