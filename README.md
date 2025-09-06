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

#### Option A: Flask-Login Integrated System (Recommended)
```bash
# Start the integrated frontend + backend system with Flask-Login
python scripts/start_flask_login.py
```

#### Option B: Simple Authentication System
```bash
# Start the integrated frontend + backend system with simple auth
python scripts/start_frontend.py
```

#### Option C: Separate Services
```bash
# Terminal 1 - Main API server with frontend
python src/main_server.py

# Terminal 2 - Streamlit dashboard (optional)
streamlit run src/dashboard/streamlit_app.py
```

### 4. Access the Platform
- **🏠 Landing Page**: http://localhost:5000
- **🔐 Login**: http://localhost:5000/login.html
- **📝 Signup**: http://localhost:5000/signup.html
- **📊 Dashboard**: http://localhost:5000/dashboard.html
- **🔧 API**: http://localhost:5000/api/health
- **📈 Streamlit Dashboard**: http://localhost:8501 (if running)
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
- [Frontend Integration Guide](docs/FRONTEND_INTEGRATION.md)
- [API Documentation](docs/API.md)

## Features
- ✅ **Complete HTML Frontend** - Modern, responsive interface
- ✅ **Role-based Dashboards** - Student, Counselor, Faculty, Admin
- ✅ **Real-time AI Chat** - Interactive counseling bot
- ✅ **Risk Assessment Tables** - Visual risk data for counselors
- ✅ **Flask-Login Authentication** - Industry-standard session management
- ✅ **Mobile Responsive** - Works on all devices
- ✅ **SQLite Database** - No external dependencies
- ✅ **RESTful API** - Clean backend integration
