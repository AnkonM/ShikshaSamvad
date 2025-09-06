from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def get_engine(uri: str):
    return create_engine(uri, future=True)

def init_db(uri: str, schema_sql_path: str):
    engine = get_engine(uri)
    with engine.begin() as conn:
        with open(schema_sql_path, "r") as f:
            conn.execute(text(f.read()))
    return engine

def get_session(uri: str):
    engine = get_engine(uri)
    return sessionmaker(bind=engine, future=True)()