import argparse
import pandas as pd
from pathlib import Path
from src.risk_engine.preprocess import add_last_activity_days
from src.database.sqlite_db import init_db, get_engine
from src.database.firebase_db import push_document

def ingest_sqlite(df: pd.DataFrame, uri: str, schema_path: str):
    init_db(uri, schema_path)
    engine = get_engine(uri)
    df.to_sql("risk_scores", engine, if_exists="append", index=False)

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
    df = add_last_activity_days(df)
    if args.backend == "sqlite":
        ingest_sqlite(df, args.sqlite_uri, args.schema)
        print("Ingested into SQLite.")
    else:
        ingest_firebase(df, args.firebase_credentials)
        print("Ingested into Firebase.")