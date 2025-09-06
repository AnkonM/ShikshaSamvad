import streamlit as st
import pandas as pd
from pathlib import Path
from .visualizations import risk_distribution, attendance_vs_risk

st.set_page_config(page_title="Shikshasamvaad Dashboard", layout="wide")
st.title("Shikshasamvaad Wellness Dashboard")

pred_path = Path("data/processed/risk_predictions.csv")
if pred_path.exists():
    df = pd.read_csv(pred_path)
    st.success(f"Loaded predictions: {len(df)} rows")
    st.plotly_chart(risk_distribution(df), use_container_width=True)
    st.plotly_chart(attendance_vs_risk(df), use_container_width=True)
    high_risk = df[df["dropout_risk"] >= 0.7].copy()
    high_risk["anon_id"] = high_risk["student_id"].apply(lambda s: hash(s) % 100000)
    st.subheader("High-Risk Students (Anonymized)")
    st.dataframe(high_risk[["anon_id", "course", "dropout_risk", "risk_ci_lower", "risk_ci_upper"]])
else:
    st.warning("No predictions found. Generate data and run training/inference.")