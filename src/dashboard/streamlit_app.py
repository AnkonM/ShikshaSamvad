import streamlit as st
import pandas as pd
from pathlib import Path
from src.dashboard.visualizations import risk_distribution, attendance_vs_risk, course_trend, attribute_strengths
import requests
import json

st.set_page_config(page_title="Shikshasamvad Dashboard", layout="wide")

# Simple authentication check
if 'user' not in st.session_state:
    st.title("Login Required")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            try:
                response = requests.post("http://localhost:5000/api/auth/login", 
                                       json={"email": email, "password": password})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.user = data['user']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Login failed. Please check your credentials.")
            except:
                st.error("Cannot connect to authentication service.")
    
    with col2:
        st.subheader("Register")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_first_name = st.text_input("First Name")
        reg_last_name = st.text_input("Last Name")
        reg_role = st.selectbox("Role", ["student", "counselor", "faculty", "admin"])
        
        if st.button("Register"):
            try:
                response = requests.post("http://localhost:5000/api/auth/register", 
                                       json={
                                           "email": reg_email,
                                           "password": reg_password,
                                           "first_name": reg_first_name,
                                           "last_name": reg_last_name,
                                           "role": reg_role
                                       })
                if response.status_code == 201:
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed.")
            except:
                st.error("Cannot connect to authentication service.")
    
    st.stop()

# Main dashboard content
user = st.session_state.user
st.title(f"Shikshasamvad Wellness Dashboard - Welcome {user['first_name']}!")

# Logout button
if st.button("Logout"):
    try:
        requests.post("http://localhost:5000/api/auth/logout")
        del st.session_state.user
        st.rerun()
    except:
        st.error("Logout failed")

# Role-based content
if user['role'] == 'student':
    st.info("Student Dashboard - View your own data")
elif user['role'] == 'counselor':
    st.info("Counselor Dashboard - View assigned students")
elif user['role'] == 'faculty':
    st.info("Faculty Dashboard - View class reports")
elif user['role'] == 'admin':
    st.info("Admin Dashboard - Full system access")

pred_path = Path("data/processed/risk_predictions.csv")
df_pred = pd.read_csv(pred_path) if pred_path.exists() else pd.DataFrame()

raw_dir = Path("data/raw")
assess_path = raw_dir / "assessments.csv"
courses_path = raw_dir / "courses.csv"

df_assess = pd.read_csv(assess_path) if assess_path.exists() else pd.DataFrame()
df_courses = pd.read_csv(courses_path) if courses_path.exists() else pd.DataFrame()

colA, colB = st.columns(2)

with colA:
    st.subheader("Performance Summary")
    if not df_pred.empty:
        # For students, filter to their id if available
        if user['role'] == 'student' and 'student_id' in user and user['student_id']:
            df_view = df_pred[df_pred["student_id"] == user['student_id']]
        else:
            df_view = df_pred.copy()
        st.plotly_chart(risk_distribution(df_view), use_container_width=True)
        st.plotly_chart(attendance_vs_risk(df_view), use_container_width=True)
        high_risk = df_view[df_view["dropout_risk"] >= 0.7].copy()
        if not high_risk.empty:
            high_risk["anon_id"] = high_risk["student_id"].apply(lambda s: hash(s) % 100000)
            st.subheader("High-Risk Students (Anonymized)")
            st.dataframe(high_risk[["anon_id", "course", "dropout_risk", "risk_ci_lower", "risk_ci_upper"]])
    else:
        st.warning("No predictions found. Generate data and ingest.")

with colB:
    st.subheader("Course Trends and Attributes")
    if df_assess.empty or df_courses.empty:
        st.info("Assessments or courses data not found. Run data generation.")
    else:
        # Student scope
        student_id = st.text_input("Student ID", value=(user.get('student_id') or 'S1000'))
        course_codes = sorted(df_courses["course_code"].unique())
        course_code = st.selectbox("Select course", course_codes)
        st.plotly_chart(course_trend(df_assess, student_id, course_code), use_container_width=True)
        st.plotly_chart(attribute_strengths(df_courses, course_code), use_container_width=True)

st.divider()
st.subheader("BNN Dropout Risk")
if not df_pred.empty:
    # Show a per-student summary row
    if user['role'] == 'student' and user.get('student_id'):
        sview = df_pred[df_pred["student_id"] == user['student_id']][["course", "dropout_risk", "risk_ci_lower", "risk_ci_upper"]]
        st.dataframe(sview)
    else:
        st.dataframe(df_pred[["student_id", "course", "dropout_risk", "risk_ci_lower", "risk_ci_upper"]].head(50))
else:
    st.info("No BNN risk predictions available yet.")

st.divider()
st.subheader("NLP Chatbot")
st.caption("This will open a chat interface in a modal/pop-out.")
if st.button("Open Chatbot"):
    st.info("Chatbot pop-out coming soon...")