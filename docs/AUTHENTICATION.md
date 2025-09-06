# 🔐 ShikshaSamvad Authentication System

## Overview

The ShikshaSamvad authentication system provides secure, role-based access control for the student wellness platform. It supports multiple user types with different permission levels and integrates seamlessly with existing services.

## 🏗️ Architecture

### Components

- **User Management**: Registration, login, profile management
- **Role-Based Access Control (RBAC)**: Student, Counselor, Faculty, Admin roles
- **JWT Authentication**: Secure token-based authentication
- **Session Management**: Multi-device session tracking
- **Password Security**: Bcrypt hashing, strength validation
- **Rate Limiting**: Protection against brute force attacks

### Database Schema

```sql
-- Users table with role-based access
users (id, email, username, password_hash, role, status, ...)

-- Session management
user_sessions (id, user_id, session_token, refresh_token, ...)

-- Password reset tokens
password_reset_tokens (id, user_id, token, expires_at, ...)
```

## 👥 User Roles & Permissions

| Role | Permissions | Access Level |
|------|-------------|--------------|
| **Student** | View own data, chat with bot, view own risk scores | Limited |
| **Counselor** | View assigned students, access chat logs, moderate content | Medium |
| **Faculty** | View class risk reports, student alerts | Medium |
| **Admin** | Full system access, user management, analytics | Full |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Authentication

```bash
python scripts/setup_auth.py
```

### 3. Start Authentication Server

```bash
python src/auth/server.py
```

The server will run on `http://localhost:5000`

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login user | No |
| POST | `/api/auth/logout` | Logout user | Yes |
| POST | `/api/auth/refresh` | Refresh access token | No |
| GET | `/api/auth/me` | Get current user info | Yes |
| POST | `/api/auth/change-password` | Change password | Yes |
| POST | `/api/auth/forgot-password` | Request password reset | No |
| POST | `/api/auth/reset-password` | Reset password with token | No |

### Protected Services

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|---------------|
| POST | `/api/chatbot/chat` | Chat with bot | Student+ |
| GET | `/api/chatbot/logs` | View chat logs | Counselor+ |
| GET | `/api/dashboard/risk-data` | View risk data | Student+ |
| GET | `/api/dashboard/students` | View students list | Faculty+ |
| POST | `/api/risk/predict` | Generate predictions | Counselor+ |
| POST | `/api/risk/train` | Train model | Admin |

## 🔧 Configuration

### Environment Variables

```bash
# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Policy
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=true
REQUIRE_LOWERCASE=true
REQUIRE_NUMBERS=true
REQUIRE_SPECIAL_CHARS=true

# Security
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Not in common passwords list

## 🔒 Security Features

### Authentication Security

- **JWT Tokens**: Secure, stateless authentication
- **Refresh Tokens**: Long-lived tokens for seamless experience
- **Password Hashing**: Bcrypt with salt
- **Rate Limiting**: Protection against brute force
- **Account Lockout**: Temporary lockout after failed attempts
- **Session Management**: Multi-device session tracking

### API Security

- **CORS Protection**: Configurable allowed origins
- **Security Headers**: XSS, CSRF, and clickjacking protection
- **Input Validation**: Comprehensive input sanitization
- **Role-Based Access**: Granular permission system

## 📱 Frontend Integration

### React/Vue Integration Example

```javascript
// Login
const login = async (email, password) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  if (data.access_token) {
    localStorage.setItem('access_token', data.access_token);
  }
};

// Protected API calls
const apiCall = async (endpoint) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(endpoint, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

### Token Management

```javascript
// Auto-refresh token
const refreshToken = async () => {
  const response = await fetch('/api/auth/refresh', {
    method: 'POST',
    credentials: 'include'
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
  }
};

// Interceptor for automatic token refresh
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      await refreshToken();
      return axios.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

## 🧪 Testing

### Test Authentication

```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "username": "student123",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "student_id": "S1001"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123!"
  }'

# Access protected endpoint
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔄 Integration with Existing Services

### Chatbot Integration

The chatbot service now requires authentication:

```python
from src.auth.middleware import require_auth

@app.route('/api/chatbot/chat', methods=['POST'])
@require_auth
def chat():
    # Chat logic with authenticated user context
    user = g.current_user
    # ... existing chat logic
```

### Dashboard Integration

Role-based data access:

```python
from src.auth.middleware import require_permission

@app.route('/api/dashboard/risk-data', methods=['GET'])
@require_auth
def get_risk_data():
    # Returns data based on user role
    # Students: own data only
    # Counselors: assigned students
    # Admin: all data
```

## 🚨 Security Considerations

### Production Deployment

1. **Change Secret Key**: Use a strong, unique secret key
2. **Enable HTTPS**: Use SSL certificates
3. **Secure Cookies**: Set `secure=True` for HTTPS
4. **Environment Variables**: Store sensitive config in env vars
5. **Database Security**: Use connection pooling and encryption
6. **Rate Limiting**: Implement Redis-based rate limiting
7. **Logging**: Monitor authentication attempts and failures

### Monitoring

- Failed login attempts
- Account lockouts
- Suspicious activity patterns
- Token usage and refresh patterns

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Errors**: Check database connection and schema
3. **Token Errors**: Verify JWT secret key configuration
4. **CORS Errors**: Check allowed origins configuration

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Additional Resources

- [JWT.io](https://jwt.io/) - JWT token debugging
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Flask-Security Documentation](https://flask-security.readthedocs.io/)

## 🤝 Contributing

When adding new features:

1. Follow the existing code structure
2. Add appropriate tests
3. Update documentation
4. Consider security implications
5. Test with different user roles

---

**Note**: This authentication system is designed for the ShikshaSamvad project and integrates with existing risk prediction, chatbot, and dashboard services.
