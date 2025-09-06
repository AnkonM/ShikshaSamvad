from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def get_engine(uri: str):
    return create_engine(uri, future=True)

def init_db(uri: str, schema_sql_path: str):
    engine = get_engine(uri)
    with engine.begin() as conn:
        with open(schema_sql_path, "r") as f:
            sql_content = f.read()
            # Split by semicolon and execute each statement separately
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            for statement in statements:
                conn.execute(text(statement))
    return engine

def get_session(uri: str):
    engine = get_engine(uri)
    return sessionmaker(bind=engine, future=True)()