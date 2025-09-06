import pandas as pd
import plotly.express as px

def risk_distribution(df: pd.DataFrame):
    return px.histogram(df, x="dropout_risk", nbins=20, title="Dropout Risk Distribution")

def attendance_vs_risk(df: pd.DataFrame):
    return px.scatter(df, x="attendance", y="dropout_risk", title="Attendance vs Dropout Risk")