import pandas as pd

def clean_column_names(df):
    """
    Clean column names
    """
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    return df

def clean_text_cols(df):
    """
    remove empty space and lowercase column  names
    """

    text_cols = ["name", "gender", "event", "meet", "atmosphere", "race_type", "season", "performance_type"]

    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    df["event"] = df["event"].str.lower()

    return df

def convert_datatypes(df):
    """
    Convert datatypes of columns properly
    """

    category_cols = ["gender", "grade", "athlete_class", "event", "meet", "atmosphere", "race_type", "season", "performance_type"]

    for col in category_cols:
        df[col] = df[col].astype("category")

    return df

def clean_data(df):
    df = clean_column_names(df)
    df = clean_text_cols(df)
    df = convert_datatypes(df)

    return df
