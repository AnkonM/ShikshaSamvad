# ShikshaSamvad
AI/ML-based Student Dropout Prediction and Counseling Platform

## Overview
ShikshaSamvad is an integrated platform for early detection of student dropout risk and continuous well-being support. It combines a Bayesian Neural Network risk assessment engine, an NLP counseling chatbot, and a role-based wellness dashboard with simple authentication.

## Key Components
- **AI Risk Assessment Engine**: Bayesian Neural Network predicting dropout probability with uncertainty intervals
- **NLP Counseling Chatbot**: Flask API providing CBT-inspired tips, mindfulness, and crisis escalation
- **Wellness Dashboard**: Streamlit app with role-based access (Student, Counselor, Faculty, Admin)
- **Simple Authentication**: Session-based auth with role-based permissions
- **Database**: SQLite for lightweight deployment

## Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize System
```bash
# Setup authentication and generate sample data
python scripts/setup_simple_auth.py
```

### 3. Start Services
```bash
# Terminal 1 - Main API server
python src/main_server.py

# Terminal 2 - Dashboard
streamlit run src/dashboard/streamlit_app.py
```

### 4. Access the Platform
- **API**: http://localhost:5000
- **Dashboard**: http://localhost:8501
- **Default Admin**: admin@shikshasamvaad.com / admin123

## User Roles
- **Student**: View own data, chat with bot
- **Counselor**: View assigned students, access chat logs
- **Faculty**: View class reports, student alerts
- **Admin**: Full system access, user management

## API Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/chatbot/chat` - Chat with bot
- `GET /api/dashboard/risk-data` - Get risk data
- `POST /api/risk/predict` - Generate predictions

## Documentation
- [Simple Authentication Guide](docs/SIMPLE_AUTH.md)
- [API Documentation](docs/API.md)

## Features
- ✅ Simple session-based authentication
- ✅ Role-based access control
- ✅ Real-time risk prediction
- ✅ Interactive chatbot
- ✅ Comprehensive dashboard
- ✅ SQLite database (no external dependencies)
