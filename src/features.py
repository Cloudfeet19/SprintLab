import pandas as pd

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    applies classification of events and establishes what direction determines a better result
    updates the df with a universal results column
    updates the df with is_pr, current_pr, and improvement columns

    :param df: Master df
    :return: returns the updates dataframe
    """
    # Apply classification of events and establish what direction determines a better result
    df["event_type"] = df["event"].apply(_classify_event).astype("category")
    df["better_direction"] = df["event_type"].apply(_better_direction).astype("category")

    # Universal Results Column
    df["result_value"] = df["result_in_seconds"].fillna(df["result_in_meters"])

    # updates the temporary df with is_pr, current_pr, and improvement column
    pr_df = (
        df.groupby(["athlete_id", "event"], group_keys=False, observed=True)
          .apply(_detect_pr_progression)
    )

    # Return elements to their original index so that adding them to the original df is correct
    pr_df = pr_df.sort_index()

    # add pr columns using the temp df
    df[["is_pr", "current_pr", "improvement"]] = pr_df[["is_pr", "current_pr", "improvement"]]

    return df

# Classify Event
def _classify_event(event: str) -> str:
    """
    :param event: event that is being classified
    :return: classification of event
    """
    track_events = ["60m", "60mh", "100m", "100mh", "110mh", "200m", "300mh", "400m", "800m", "1600m", "3200m"]
    field_events = ["long jump", "triple jump", "high jump", "javelin", "pole vault", "shot put", "discus"]

    if event in track_events:
        return "track"
    elif event in field_events:
        return "field"
    else:
        return "other"

# Better Direction Logic
def _better_direction(event_type: str) -> str:
    """
    :param event_type: field or track event
    :return: determines what direction is considered a better result
    """

    if event_type == "track":
        return "lower"
    elif event_type == "field":
        return "higher"
    else:
        return "unknown"

# Sort dataframe by athlete, event, and date
def _detect_pr_progression(athlete_event_dataset: pd.DataFrame):
    """
    Determines if a result in the dataframe is a personal best based on previous results
    Captures the current PR
    Calculates the improvement of every PR

    :param athlete_event_dataset: Dataset grouping athlete and event
    :return: returns an updated version of the passed in dataset with the new columns 'is_pr', 'current_pr', and 'improvement'
    """
    athlete_event_dataset = athlete_event_dataset.sort_values("date", ascending=True).copy()

    best_so_far = None # placeholder for best result up until a certain point
    pr_list = [] # Determines if a result in the df is a result based on previous results
    current_pr_list = [] # Captures the current PR
    improvement_list = [] # Calculate the improvement of every pr

    # grabs the better direction for a more easily readable variable
    direction = athlete_event_dataset["better_direction"].iloc[0]

    # detect pr logic
    for result in athlete_event_dataset["result_value"]:
        # checks if this is the first result recorded
        if best_so_far == None:
            # if so, update best_so_far, pr_list, and improvement_list accordingly
            best_so_far = result
            pr_list.append(True)
            improvement_list.append(None)

        # otherwise figure out what direction determines a better result
        else:
            if direction == "lower": # Track event
                if result < best_so_far:
                    # if result is lower than best so far, personal best
                    # update pr_list and improvement_list accordingly
                    pr_list.append(True)

                    improvement = result - best_so_far # Calculate the improvement from the last pr
                    improvement_list.append(improvement)

                    best_so_far = result
                else:
                    # otherwise no personal best
                    pr_list.append(False)
                    improvement_list.append(None)

            elif direction == "higher": # Field event
                if result > best_so_far:
                    # if result is higher than best so far, personal best
                    # update pr_list and improvement_list accordingly
                    pr_list.append(True)

                    improvement = result - best_so_far # Calculate the improvement from the last pr
                    improvement_list.append(improvement)

                    best_so_far = result
                else:
                    # otherwise no personal best
                    # update pr_list and improvement_list accordingly
                    pr_list.append(False)
                    improvement_list.append(None)

        current_pr_list.append(best_so_far)

    # updates the passed in dataset with the new columns / data
    athlete_event_dataset["is_pr"] = pr_list
    athlete_event_dataset["current_pr"] = current_pr_list
    athlete_event_dataset["improvement"] = improvement_list

    return athlete_event_dataset