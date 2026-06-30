import pandas as pd
from sqlalchemy import select

from database.models import db, AthleteTable, ResultTable
from src.cleaning import clean_data
from src.features import add_features

def initialize_dataset(db, user_id):
    # Gets all results for each athlete in the database
    rows = db.session.execute(
        select(AthleteTable, ResultTable)
        .join(ResultTable, AthleteTable.id == ResultTable.athlete_id)
        .where(AthleteTable.user_id == user_id)
    ).all()

        # build df from rows

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