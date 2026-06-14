import pandas as pd

def athletes_summary(df: pd.DataFrame, athlete_id: int) -> dict:
    """
    Find total performances
    Find medal count -- Add State Medal Count Later
    Find total pr's
    Find current pr's
    Determine best event

    :param df: Master df
    :param athlete_id: ID for the desired athlete
    :return: dictionary with name, total performances, medal count, total personal best performances, current personal bests, main events
    """

    athlete_df = df[df["athlete_id"] == athlete_id]

    name = athlete_df["name"].iloc[0]
    total_performances = athlete_df.raw_result.count()
    gold_medal_count = athlete_df["placement"].isin([1]).sum()
    silver_medal_count = athlete_df["placement"].isin([2]).sum()
    bronze_medal_count = athlete_df["placement"].isin([3]).sum()
    total_medal_count = gold_medal_count + silver_medal_count + bronze_medal_count
    total_prs = athlete_df["is_pr"].sum()
    current_prs = {}

    event_df = athlete_df.groupby("event", as_index=False, observed=True)

    current_prs = _get_prs(event_df) # Grabs the current prs

    main_events = _get_main_event(athlete_df) # Grabs a ranked dictionary determined by average placement per event

    summary = {
        "name" : name,
        "total_performances" : total_performances,
        "gold_medal_count" : gold_medal_count,
        "silver_medal_count" : silver_medal_count,
        "bronze_medal_count" : bronze_medal_count,
        "total_medal_count" : total_medal_count,
        "total_prs" : total_prs,
        "current_prs" : current_prs,
        "main_event(s)" : main_events
    }

    return summary

def _get_main_event(athlete_df) -> list:
    """
    Returns best event(s) based on average placement
    """
    avg_placement = athlete_df.groupby("event", observed=True)["placement"].mean()

    best_event_value = avg_placement.min()

    best_events = avg_placement[avg_placement == best_event_value].index.tolist()

    return best_events

def _get_prs(event_df):
    current_prs = {}

    for event_key, performance in event_df:
        event_type = performance["event_type"].iloc[0]
        event = performance["event"].iloc[0]

        if event_type == "field":
            pr_idx = performance["result_value"].idxmax()
        elif event_type == "track":
            pr_idx = performance["result_value"].idxmin()

        pr = performance.loc[pr_idx, "raw_result"]

        current_prs[event] = pr


    return current_prs

def ranking_coached_events(df):
    """
    Returns a sorted dataframe of ranked events by average placement across all results for that event
    """
    event_df = df.groupby("event", as_index=False, observed=True)

    coached_events = {}

    for event_key, event in event_df:
        performance_count = event.shape[0]
        avg_placement = float(round(event["placement"].mean(), 2))
        event = event["event"].iloc[0]

        coached_events[event] = {"avg_placement" : avg_placement,
                                 "result_count" : performance_count}

    ranked_coaching_events = sorted(coached_events.items(), key=lambda item: item[1]["avg_placement"])

    ranked_events_df = ranked_events_df = pd.DataFrame([
        {
            "event": event,
            "avg_placement": data["avg_placement"],
            "result_count": data["result_count"]
        }
        for event, data in ranked_coaching_events
    ])

    return ranked_events_df




