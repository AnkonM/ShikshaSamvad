import pandas as pd
from datetime import datetime

def add_last_activity_days(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["last_activity"] = pd.to_datetime(df["last_activity"])
    df["last_activity_days"] = (pd.Timestamp(datetime.today().date()) - df["last_activity"]).dt.days
    return df

def select_features(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["attendance", "avg_grade", "submissions", "last_activity_days"]
    return df[cols].copy()