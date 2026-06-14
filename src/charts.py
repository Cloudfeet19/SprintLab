import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

def athlete_event_result_chart(df: pd.DataFrame, athlete_id: int, event: str) -> px.line:
    """
    :param df: master dataframe
    :param athlete_id: ID of the desired athlete
    :param event: Desired event to display
    :return: returns the line chart of an athletes result data for the specified event
    """
    # filters the df by grouping the desired athlete and event and sorting the results by date
    filtered_df = df[
        (df["athlete_id"] == athlete_id) &
        (df["event"] == event)
        ].sort_values("date")

    # guard clause to ensure that nothing else runs if no results are detected for that Athlete/Event combination
    if filtered_df.empty:
        print("Athlete/Event combo has no results")
        return None

    # grabs the name, event, and better_direction for future display purposes
    name = filtered_df["name"].iloc[0]
    event = filtered_df["event"].iloc[0]
    better_direction = filtered_df["better_direction"].iloc[0]

    # creates the line chart
    performance_line = px.line(filtered_df, x="date", y="result_value", markers=True, hover_data=["meet", "raw_result", "placement", "wind", "atmosphere", "race_type"], title=f"Athlete: {name}\n Event: {event.title()}")

    # determines the orientation of the graph depending on the better direction
    if better_direction == "lower":
        performance_line.update_yaxes(autorange="reversed")
        performance_line.update_layout(xaxis_title="Date", yaxis_title = "Seconds")
    else:
        performance_line.update_layout(xaxis_title="Date", yaxis_title = "Meters")

    return performance_line

def current_pr_progression_chart(df: pd.DataFrame, athlete_id: int, event: str) -> px.line:
    """
    :param df: master dataframe
    :param athlete_id: ID of the desired athlete
    :param event: Desired event to display
    :return: line chart data of athletes progression in the specified event

    Showcases the timeline of personal best from a single athlete in a single event
    """

    # filters the df by grouping the desired athlete and event and sorting the results by date
    filtered_df = df[
        (df["athlete_id"] == athlete_id) &
        (df["event"] == event)
        ].sort_values("date")

    # guard clause to ensure that nothing else runs if no results are detected for that Athlete/Event combination
    if filtered_df.empty:
        print("Athlete/Event combo has no results")
        return None

    # grabs all personal best performances
    filtered_df = filtered_df[filtered_df["is_pr"] == True]

    # a list of hover data for display purposes
    hover_data = ["meet", "placement", "wind", "atmosphere", "race_type", "raw_result"]

    # grabs the name, event, and better_direction for future display purposes
    name = filtered_df["name"].iloc[0]
    event = filtered_df["event"].iloc[0]
    better_direction = filtered_df["better_direction"].iloc[0]

    # creates the line chart
    progression_line = px.line(filtered_df, x="date", y="result_value", hover_data=hover_data, title=f"{name}'s {event.title()} Progression", markers=True)

    # determines the orientation of the graph depending on the better direction
    if better_direction == "lower":
        progression_line.update_yaxes(autorange="reversed")
        progression_line.update_layout(xaxis_title="Date", yaxis_title = "Seconds")
    else:
        progression_line.update_layout(xaxis_title="Date", yaxis_title = "Meters")


    return progression_line

def medal_count_chart(df: pd.DataFrame, athlete_id: int) -> px.bar:
    """
    :param df: Master df
    :param athlete_id: ID of the desired athlete
    :return: Bar chart showcasing all medals obtained by the athlete
    """

    # filters dataset to desired athlete
    athlete_dataset = df[df["athlete_id"] == athlete_id]

    # filters the dataset to all results that finished with a medal
    medal_df = athlete_dataset[athlete_dataset["placement"].isin([1, 2, 3])].copy()

    # grabs the athletes name for future display purposes
    name = athlete_dataset["name"].iloc[0]

    # grabbing all medal placements
    medal_counts = medal_df["placement"].value_counts().sort_index().reset_index()
    medal_counts.columns = ["placement", "count"]

    # creating label for future display purposes
    medal_counts["label"] = medal_counts["count"].astype(str) + " medals"

    # mapping the numerical value of a medal to a string value describing the placement of the result
    medal_counts["placement"] = medal_counts["placement"].astype(str)
    medal_counts["medal"] = medal_counts["placement"].map({
        "1" : "Gold",
        "2" : "Silver",
        "3" : "Bronze"
        })

    # creates the bar chart
    medal_chart = px.bar(
        medal_counts,
        x="placement",
        y="count",
        color="medal",
        color_discrete_map= {
            "Gold" : "#FFD700",
            "Silver" : "#C0C0C0",
            "Bronze" : "#CE8946"
        },
        title= f"{name}'s High School Career Medal Count",
        text="label"
    )

    return medal_chart

def coaching_event_rankings_chart(ranked_events_df: pd.DataFrame) -> px.bar:
    """
    :param ranked_events_df: dataset with the average placement per event
    :return: bar chart showcasing the best placements on average for all coached athletes

    This can help determine a coaches best event once all results data is inputted into the dataset
    """

    # creates label for display purposes
    ranked_events_df["label"] = ranked_events_df["result_count"].astype(str) + " results"

    # creates the bar chart
    ranking_bar = px.bar(
        ranked_events_df,
        x="event",
        y="avg_placement",
        color="event",
        hover_data=["result_count"],
        title="Coached Events Ranked by Average Placement",
        labels={
            "event": "Event",
            "avg_placement": "Average Placement",
            "result_count": "Number of Results"
        },
        text="label",
    )

    # Updating the axis titles
    ranking_bar.update_xaxes(title="Event")
    ranking_bar.update_yaxes(title="Average Placement")

    return ranking_bar
