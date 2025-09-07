from pathlib import Path
import pandas as pd

def generate_report_csv(df: pd.DataFrame, output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return str(out)

def generate_report_pdf(df: pd.DataFrame, output_path: str) -> str:
    # Placeholder: switch to reportlab/fpdf2 as needed
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        f.write("Shikshasamvad Report (placeholder)\n")
        f.write(f"Rows: {len(df)}\n")
    return str(out)