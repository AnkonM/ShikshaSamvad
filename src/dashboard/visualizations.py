import pandas as pd
import plotly.express as px
import json

def risk_distribution(df: pd.DataFrame):
    return px.histogram(df, x="dropout_risk", nbins=20, title="Dropout Risk Distribution")

def attendance_vs_risk(df: pd.DataFrame):
    return px.scatter(df, x="attendance", y="dropout_risk", title="Attendance vs Dropout Risk")

def course_trend(df_assess: pd.DataFrame, student_id: str, course_code: str):
    d = df_assess[(df_assess["student_id"] == student_id) & (df_assess["course_code"] == course_code)].copy()
    if d.empty:
        return px.line(title="No assessments available")
    d = d.sort_values("submitted_at")
    return px.line(d, x="submitted_at", y="score", color="assessment_type", markers=True,
                   title=f"Assessment Trend - {course_code}")

def attribute_strengths(df_courses: pd.DataFrame, course_code: str):
    row = df_courses[df_courses["course_code"] == course_code]
    if row.empty:
        return px.bar(title="No attributes available")
    attrs = json.loads(row.iloc[0]["attributes_json"]) if "attributes_json" in row.columns else {}
    if not attrs:
        return px.bar(title="No attributes available")
    adf = pd.DataFrame({"attribute": list(attrs.keys()), "weight": list(attrs.values())})
    return px.bar(adf, x="attribute", y="weight", title=f"Course Attributes - {course_code}")