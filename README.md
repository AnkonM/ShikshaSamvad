# ShikshaSamvad
AI/ML-based Student Dropout Prediction and Counseling Platform

## Overview
ShikshaSamvad is an integrated platform for early detection of student dropout risk and continuous well-being support. It combines a Bayesian Neural Network risk assessment engine, an NLP counseling chatbot, and a role-based wellness dashboard with Flask-Login authentication.

## Key Components
- **AI Risk Assessment Engine**: Bayesian Neural Network predicting dropout probability with uncertainty intervals
- **NLP Counseling Chatbot**: Flask API providing CBT-inspired tips, mindfulness, and crisis escalation
- **Wellness Dashboard**: Flask-powered dashboard (Chart.js) with role-based access (Student, Counselor, Faculty, Admin)
- **Flask-Login Authentication**: Industry-standard session-based authentication with role-based permissions
- **Extended LMS Data**: Detailed course attributes, assessments, submissions, and attendance tracking
- **Database**: SQLite for lightweight deployment

---

## Prerequisites

- **Python 3.9+**
- **pip** (Python package manager)
- **bash** (for running shell scripts on Unix-like systems)

---

## Installation & Setup

### 1. Clone or Navigate to Project Directory
```bash
cd /Users/angong/Documents/SIH25/ShikshaSamvad
```

### 2. Create and Activate Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
# .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install all required packages
pip install -r requirements.txt
```

### 4. Set Environment Variables
```bash
# Set PYTHONPATH to project root (required for imports)
export PYTHONPATH="/Users/angong/Documents/SIH25/ShikshaSamvad"

# Add to your ~/.zshrc or ~/.bashrc for persistence:
# echo 'export PYTHONPATH="/Users/angong/Documents/SIH25/ShikshaSamvad"' >> ~/.zshrc
```

---

## Data Generation & Ingestion

### Generate LMS Data
The system requires detailed LMS data including courses, assessments, submissions, and attendance records.

```bash
# Generate synthetic LMS datasets
python scripts/generate_lms_data.py
```

This creates the following CSV files in `data/raw/`:
- `lms_data.csv` - Aggregated summary data
- `courses.csv` - Course definitions with attribute weights
- `assessments.csv` - Individual assessment records with scores
- `submissions.csv` - Submission tracking with timestamps
- `attendance.csv` - Daily attendance records

### Ingest Data into Database

```bash
# Ingest data into SQLite database
# Use --clear flag to replace existing data
python scripts/ingest_lms_data.py \
  --backend sqlite \
  --sqlite_uri sqlite:///data/processed/shikshasamvad.db \
  --schema src/database/schema.sql \
  --extended \
  --clear
```

**Options:**
- `--extended`: Ingest extended LMS tables (courses, assessments, submissions, attendance)
- `--clear`: Clear existing transactional data before ingesting (recommended for fresh start)
- Without `--clear`: Append new data to existing records

### Initialize Authentication System
```bash
# Setup authentication tables and default admin user
python scripts/setup_simple_auth.py
```

This creates:
- User authentication tables
- Default admin user: `admin@shikshasamvad.com` / `admin123`

---

## Running the System

### Integrated Flask System (Recommended)

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Set PYTHONPATH for module imports
export PYTHONPATH="/Users/angong/Documents/SIH25/ShikshaSamvad"

# Start the complete Flask-based platform
python scripts/start_flask_login.py
```

This command:
- ✅ Starts the Flask server on `http://localhost:5000`
- ✅ Initializes the SQLite database if needed
- ✅ Creates the default admin user if missing
- ✅ Serves the analytics dashboard directly at `/dashboard.html`

### Manual Start (advanced)

```bash
source .venv/bin/activate
export PYTHONPATH="/Users/angong/Documents/SIH25/ShikshaSamvad"
python src/main_server.py
```

> **Legacy Streamlit Prototype**: If you still need the old Streamlit dashboard, run `bash scripts/run_dashboard.sh` in another terminal. This is optional and no longer part of the default workflow.

---

## Access Points

Once the system is running, access the following URLs:

### Web Interface
- **🏠 Landing Page**: http://localhost:5000
- **🔐 Login Page**: http://localhost:5000/login.html
- **📝 Signup Page**: http://localhost:5000/signup.html
- **📊 HTML Dashboard**: http://localhost:5000/dashboard.html
- **📈 Analytics Dashboard**: http://localhost:5000/dashboard.html

### API Endpoints
- **Health Check**: http://localhost:5000/api/health
- **Auth Status**: http://localhost:5000/api/auth/me (requires login)

### Default Credentials
- **Email**: `admin@shikshasamvad.com`
- **Password**: `admin123`
- **Role**: `admin`

---

## Dashboard Features

### Student Dashboard
- **Performance Summary**: Attendance and grade overview
- **Course Trend Analysis**: Select a course to view assessment trends over time
- **Strengths & Weaknesses**: Visual breakdown of course attributes (problem solving, retention, etc.)
- **BNN Dropout Risk**: Display of calculated dropout risk with confidence intervals
- **AI Chatbot**: Pop-out button for NLP counseling chatbot

### Counselor Dashboard
- **Student Risk Assessments**: View all students with risk levels
- **Risk Data Tables**: Detailed risk scores per student/course
- **Student Management**: Access to student profiles and intervention tools

### Faculty Dashboard
- **Class Reports**: Overview of class performance
- **Student Alerts**: Notifications for at-risk students
- **Analytics**: Performance trends and insights

### Admin Dashboard
- **System Statistics**: Total users, active sessions, risk alerts
- **User Management**: Create, update, and manage user accounts
- **System Monitoring**: Full system access and configuration

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
  }
  ```

- `POST /api/auth/login` - Login user
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "remember": true
  }
  ```

- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info (requires authentication)
- `POST /api/auth/change-password` - Change password (requires authentication)

### Chatbot
- `POST /api/chatbot/chat` - Chat with AI counselor (requires authentication)
  ```json
  {
    "text": "I'm feeling stressed about exams"
  }
  ```

- `POST /api/chatbot/analyze` - Analyze text sentiment (requires authentication)

### Dashboard
- `GET /api/dashboard/risk-data` - Get risk assessment data (requires authentication)
- `GET /api/dashboard/students` - Get students list (counselor/faculty/admin only)

### Risk Engine
- `POST /api/risk/predict` - Generate risk predictions (counselor/admin only)
- `POST /api/risk/train` - Train BNN model (admin only)

---

## Project Structure

```
ShikshaSamvad/
├── config/                 # Configuration files
│   ├── rasa_config.yml
│   └── settings.yaml
├── data/
│   ├── raw/               # Generated CSV data files
│   │   ├── lms_data.csv
│   │   ├── courses.csv
│   │   ├── assessments.csv
│   │   ├── submissions.csv
│   │   └── attendance.csv
│   └── processed/         # Processed data and database
│       └── shikshasamvad.db
├── deployments/           # Docker and deployment configs
│   ├── docker-compose.yml
│   └── Dockerfile
├── docs/                  # Documentation
│   ├── FRONTEND_INTEGRATION.md
│   └── SIMPLE_AUTH.md
├── models/                # Trained ML models
│   └── risk_engine/
│       └── model.pt
├── notebooks/             # Jupyter notebooks for analysis
│   ├── bnn_experiments.ipynb
│   ├── risk_prediction.ipynb
│   └── sentiment_analysis.ipynb
├── scripts/               # Utility scripts
│   ├── generate_lms_data.py
│   ├── ingest_lms_data.py
│   ├── run_dashboard.sh
│   ├── setup_simple_auth.py
│   └── start_flask_login.py
├── src/
│   ├── chatbot/           # NLP chatbot implementation
│   │   ├── crisis_detector.py
│   │   ├── nlu_model.py
│   │   └── server.py
│   ├── dashboard/         # Flask dashboard utilities & visualizations
│   │   ├── streamlit_app.py
│   │   ├── visualizations.py
│   │   └── reports.py
│   ├── database/          # Database utilities
│   │   ├── firebase_db.py
│   │   ├── schema.sql
│   │   └── sqlite_db.py
│   ├── flask_auth.py      # Flask-Login authentication
│   ├── flask_auth_api.py  # Auth API endpoints
│   ├── main_server.py     # Main Flask application
│   ├── risk_engine/       # BNN risk prediction
│   │   ├── bnn_model.py
│   │   ├── data_loader.py
│   │   ├── predict.py
│   │   ├── preprocess.py
│   │   └── train.py
│   └── utils/             # Utility functions
│       ├── constants.py
│       ├── helpers.py
│       └── logger.py
├── static/                # HTML frontend files
│   ├── dashboard.html
│   ├── landing-page.html
│   ├── login.html
│   └── signup.html
├── tests/                 # Test files
│   ├── test_chatbot.py
│   ├── test_dashboard.py
│   ├── test_database.py
│   └── test_risk_engine.py
├── environment.yml        # Conda environment (optional)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## User Roles & Permissions

### Student
- View own performance data
- Access personal risk assessments
- Chat with AI counselor
- View course trends and attributes
- Limited to own data only

### Counselor
- View assigned students' data
- Access risk assessment tables
- View chat logs and interventions
- Manage student profiles
- Access all student data

### Faculty
- View class reports and analytics
- Access student alerts
- View performance trends
- Limited to class-level data

### Admin
- Full system access
- User management (create, update, delete)
- System configuration
- Model training and prediction
- All data access

---

## Troubleshooting

### Import Errors
**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Set PYTHONPATH before running scripts
```bash
export PYTHONPATH="/Users/angong/Documents/SIH25/ShikshaSamvad"
```

### Port Already in Use
**Problem**: `Port 5000 is already in use`

**Solution**: 
- Kill existing processes:
  ```bash
  # Find and kill Flask process
  lsof -ti:5000 | xargs kill -9
  ```
- Or change ports in the configuration files

### Database Not Found
**Problem**: `Database not found` error

**Solution**: Run setup script
```bash
python scripts/setup_simple_auth.py
```

### Duplicate Course Code Error
**Problem**: `UNIQUE constraint failed: courses.course_code`

**Solution**: Use `--clear` flag when ingesting data
```bash
python scripts/ingest_lms_data.py --extended --clear
```

### Legacy Streamlit Dashboard (Optional)
The Streamlit prototype is still available for reference. If you choose to run it and see a blank page:

1. Launch the app: `bash scripts/run_dashboard.sh`
2. Ensure `PYTHONPATH` is set
3. Verify data files exist in `data/raw/`
4. Check browser console for mixed-content or iframe errors

### Password Hashing Error
**Problem**: `AttributeError: module 'hashlib' has no attribute 'scrypt'`

**Solution**: Already fixed in code - uses `pbkdf2:sha256` method. If issue persists, ensure you're using the latest code.

---

## Production Deployment

### 1. Security Configuration
Update secret key in `src/main_server.py`:
```python
app.secret_key = 'your-secure-random-secret-key-here'  # Change this!
```

### 2. Use Production WSGI Server
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main_server:app
```

### 3. Docker Deployment
```bash
cd deployments
docker-compose up --build
```

### 4. Environment Variables
Create `.env` file:
```
SECRET_KEY=your-secret-key
DATABASE_URI=sqlite:///data/processed/shikshasamvad.db
PYTHONPATH=/path/to/ShikshaSamvad
```

### 5. Database Migration
For production, consider migrating to PostgreSQL:
- Update `DATABASE_URI` in configuration
- Update SQLAlchemy connection strings
- Run migrations

### 6. Reverse Proxy (Nginx)
Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Development

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_database.py
```

### Code Style
```bash
# Install development dependencies
pip install black flake8

# Format code
black src/ scripts/

# Lint code
flake8 src/ scripts/
```

---

## Features

- ✅ **Complete HTML Frontend** - Modern, responsive interface with Tailwind CSS
- ✅ **Role-based Dashboards** - Student, Counselor, Faculty, Admin views
- ✅ **Real-time AI Chat** - Interactive counseling bot with sentiment analysis
- ✅ **Risk Assessment Tables** - Visual risk data with confidence intervals
- ✅ **Flask-Login Authentication** - Industry-standard session management
- ✅ **Extended LMS Data** - Detailed course attributes, assessments, submissions, attendance
- ✅ **Course Trend Analysis** - Time-series visualization of student performance
- ✅ **Attribute-based Insights** - Strengths/weaknesses visualization
- ✅ **BNN Dropout Prediction** - Bayesian Neural Network with uncertainty quantification
- ✅ **Mobile Responsive** - Works on all devices
- ✅ **SQLite Database** - No external dependencies for development
- ✅ **RESTful API** - Clean backend integration

---

## Documentation

- [Simple Authentication Guide](docs/SIMPLE_AUTH.md)
- [Frontend Integration Guide](docs/FRONTEND_INTEGRATION.md)
- [API Documentation](docs/API.md) (if available)

---

## License

[Add your license information here]

---

## Contributing

[Add contribution guidelines here]

---

## Support

For issues and questions, please [open an issue](link-to-issues) or contact the development team.
