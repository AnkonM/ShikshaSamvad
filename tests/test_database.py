from pathlib import Path

def test_schema_file_exists():
    assert Path("src/database/schema.sql").exists()