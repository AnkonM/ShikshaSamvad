import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from src.risk_engine.preprocess import add_last_activity_days, select_features
from src.database.sqlite_db import init_db, get_engine
from src.database.firebase_db import push_document

def create_risk_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Convert LMS data to risk predictions for database storage"""
    df_processed = add_last_activity_days(df)
    features = select_features(df_processed)
    
    # Simple risk calculation based on features
    # Higher risk for low attendance, low grades, few submissions, long inactivity
    attendance_score = features['attendance'] / 100.0
    grade_score = features['avg_grade'] / 100.0
    submission_score = features['submissions'] / 10.0
    activity_score = np.maximum(0, 1 - features['last_activity_days'] / 30.0)
    
    # Weighted risk score (lower scores = higher risk)
    risk_score = (attendance_score * 0.3 + grade_score * 0.3 + 
                  submission_score * 0.2 + activity_score * 0.2)
    dropout_risk = 1 - risk_score  # Invert so higher values = higher risk
    
    # Add some uncertainty (confidence intervals)
    uncertainty = 0.1
    risk_ci_lower = np.maximum(0, dropout_risk - uncertainty)
    risk_ci_upper = np.minimum(1, dropout_risk + uncertainty)
    
    # Create risk predictions dataframe
    risk_df = pd.DataFrame({
        'student_id': df['student_id'],
        'course': df['course'],
        'dropout_risk': dropout_risk,
        'risk_ci_lower': risk_ci_lower,
        'risk_ci_upper': risk_ci_upper
    })
    
    return risk_df

def ingest_sqlite(df: pd.DataFrame, uri: str, schema_path: str):
    # Create the directory for the database file if it doesn't exist
    db_path = Path(uri.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    init_db(uri, schema_path)
    engine = get_engine(uri)
    
    # Convert LMS data to risk predictions
    risk_df = create_risk_predictions(df)
    risk_df.to_sql("risk_scores", engine, if_exists="append", index=False)

def ingest_firebase(df: pd.DataFrame, credentials_path: str):
    for _, row in df.iterrows():
        push_document("risk_scores", row.to_dict(), credentials_path=credentials_path)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/raw/lms_data.csv")
    ap.add_argument("--backend", choices=["sqlite","firebase"], default="sqlite")
    ap.add_argument("--sqlite_uri", default="sqlite:///data/processed/shikshasamvaad.db")
    ap.add_argument("--firebase_credentials", default="config/firebase_config.json")
    ap.add_argument("--schema", default="src/database/schema.sql")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    if args.backend == "sqlite":
        ingest_sqlite(df, args.sqlite_uri, args.schema)
        print("Risk predictions ingested into SQLite.")
    else:
        # For Firebase, also convert to risk predictions
        risk_df = create_risk_predictions(df)
        ingest_firebase(risk_df, args.firebase_credentials)
        print("Risk predictions ingested into Firebase.")