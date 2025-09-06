import streamlit as st
import pandas as pd
from pathlib import Path
from .visualizations import risk_distribution, attendance_vs_risk
import requests
import json

st.set_page_config(page_title="Shikshasamvaad Dashboard", layout="wide")

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
st.title(f"Shikshasamvaad Wellness Dashboard - Welcome {user['first_name']}!")

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