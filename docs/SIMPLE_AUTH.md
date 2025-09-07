# 🔐 Simple Authentication System

## Overview

The ShikshaSamvad project now uses an ultra-simple authentication system based on Flask sessions. This replaces the complex JWT-based system with a much lighter approach.

## Features

- ✅ **Session-based authentication** - Simple Flask sessions
- ✅ **Role-based access control** - Student, Counselor, Faculty, Admin
- ✅ **Password hashing** - SHA-256 (simple but effective)
- ✅ **User registration/login** - Basic user management
- ✅ **Protected endpoints** - Easy decorators for auth
- ✅ **CORS support** - For frontend integration

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup the system
python scripts/setup_simple_auth.py
```

### 2. Start Services

```bash
# Terminal 1 - Main API server
python src/main_server.py

# Terminal 2 - Dashboard
streamlit run src/dashboard/streamlit_app.py
```

### 3. Access the System

- **API**: http://localhost:5000
- **Dashboard**: http://localhost:8501

## Default Credentials

- **Email**: admin@shikshasamvad.com
- **Password**: admin123

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login user | No |
| POST | `/api/auth/logout` | Logout user | Yes |
| GET | `/api/auth/me` | Get current user | Yes |
| POST | `/api/chatbot/chat` | Chat with bot | Yes |
| POST | `/api/chatbot/analyze` | Analyze text | Yes |
| GET | `/api/dashboard/risk-data` | Get risk data | Yes |
| GET | `/api/dashboard/students` | Get students list | Counselor+ |
| POST | `/api/risk/predict` | Generate predictions | Counselor+ |
| POST | `/api/risk/train` | Train model | Admin |

## User Roles

| Role | Permissions |
|------|-------------|
| **Student** | View own data, chat with bot |
| **Counselor** | View assigned students, chat logs |
| **Faculty** | View class reports, student alerts |
| **Admin** | Full system access |

## Usage Examples

### Register a new user

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'
```

### Access protected endpoint

```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Cookie: session=your-session-cookie"
```

## Frontend Integration

The dashboard now includes built-in login/registration forms. For custom frontend integration:

1. **Login**: POST to `/api/auth/login` with email/password
2. **Store session**: Use the session cookie returned
3. **Make requests**: Include the session cookie in subsequent requests
4. **Logout**: POST to `/api/auth/logout`

## Security Notes

- Passwords are hashed using SHA-256
- Sessions are stored server-side
- CORS is configured for localhost development
- No JWT tokens - simpler but less scalable

## File Structure

```
src/
├── simple_auth.py          # Core authentication logic
├── simple_auth_api.py      # API endpoints
├── main_server.py          # Main server with all services
└── dashboard/
    └── streamlit_app.py    # Updated with auth
```

## Migration from Complex Auth

The complex JWT-based authentication system has been removed and replaced with this simple approach. All existing functionality is preserved but with much simpler implementation.

## Troubleshooting

1. **Database errors**: Run `python scripts/setup_simple_auth.py`
2. **Import errors**: Ensure all dependencies are installed
3. **CORS errors**: Check that origins are configured correctly
4. **Session issues**: Clear browser cookies and try again

---

This simple authentication system provides all the necessary functionality for the ShikshaSamvad project while being much easier to understand and maintain.
