from database.models import db, AthleteTable
from forms.forms import TRACK_EVENTS, FIELD_EVENTS

def query_athlete(form):
    """
    :param form: Results form
    :return: Returns the specified athlete after checking if the athlete already exists in the Database or not
    """
    first_name = form.first_name.data.strip().title()
    last_name = form.last_name.data.strip().title()
    athlete_class = form.athlete_class.data.strip()
    gender = form.gender.data.strip()
    athlete_name = f"{first_name} {last_name}"

    # assigns the first iteration of the athlete in the database to the athlete variable
    athlete = AthleteTable.query.filter_by(name=athlete_name, athlete_class=athlete_class, gender=gender).first()

    # if the athlete already exists, return that specific athlete
    if athlete:
        return athlete

    # otherwise create the new athlete and return them
    athlete = AthleteTable(
        name = athlete_name,
        gender = form.gender.data,
        athlete_class = form.athlete_class.data
    )

    db.session.add(athlete)

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

    result = result.split("-")

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
            best_result = dataset.result_value.min()
        elif dataset["better_direction"].iloc[0] == "higher":
            best_result = dataset.result_value.max()
        else:
            best_result = None

        result_data = {
            "name": name,
            "best_result": best_result
        }

        best_results.append(result_data)
    return best_results


