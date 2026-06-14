# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

import pandas as pd
from src.cleaning import clean_data
from src.features import add_features
from src.analytics import athletes_summary, ranking_coached_events
from src.charts import athlete_event_result_chart, coaching_event_rankings_chart, medal_count_chart, current_pr_progression_chart

def initialize_dataset():
    df = pd.read_csv(r"data/SprintLab_Sample_Data.csv")

    # Clean Data
    df = clean_data(df)

    # Add Features
    df = add_features(df)

    return df

df = initialize_dataset()

athlete_one = athletes_summary(df, athlete_id=1)
athlete_two = athletes_summary(df, athlete_id=2)

print(f"Athlete: {athlete_one["name"]}, PR's: {athlete_one["current_prs"]}")
print(f"Athlete: {athlete_two["name"]}, PR's: {athlete_two["current_prs"]}")

print(athlete_two)






