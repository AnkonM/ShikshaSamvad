# 🌐 Frontend Integration Guide

## Overview

The ShikshaSamvad project now includes a complete HTML frontend that integrates seamlessly with the backend API. The frontend provides a modern, responsive interface for all user roles with role-based access control.

## 🏗️ Architecture

### Frontend Structure
```
static/
├── landing-page.html    # Marketing/landing page
├── login.html          # User login form
├── signup.html         # User registration form
└── dashboard.html      # Main application dashboard
```

### Backend Integration
- **API Endpoints**: All frontend forms connect to the Flask API
- **Authentication**: Session-based auth with localStorage persistence
- **CORS**: Configured for seamless frontend-backend communication
- **Static Serving**: Flask serves HTML files directly

## 🚀 Quick Start

### 1. Start the Backend
```bash
# Terminal 1 - Start the main server
python src/main_server.py
```

### 2. Access the Frontend
- **Landing Page**: http://localhost:5000
- **Login**: http://localhost:5000/login.html
- **Signup**: http://localhost:5000/signup.html
- **Dashboard**: http://localhost:5000/dashboard.html

## 📱 Frontend Features

### Landing Page (`landing-page.html`)
- **Marketing content** with problem/solution presentation
- **Navigation** to login/signup pages
- **Responsive design** with Tailwind CSS
- **Mobile-friendly** with collapsible navigation

### Login Page (`login.html`)
- **Email/password authentication**
- **Password visibility toggle**
- **Form validation** with error handling
- **API integration** with session management
- **Automatic redirect** to dashboard on success

### Signup Page (`signup.html`)
- **User registration** with role selection
- **Password confirmation** validation
- **Form validation** with real-time feedback
- **API integration** for user creation
- **Success handling** with redirect to login

### Dashboard (`dashboard.html`)
- **Role-based content** (Student, Counselor, Faculty, Admin)
- **Real-time chat** with AI counselor
- **Risk assessment tables** for counselors
- **Performance charts** for faculty
- **System statistics** for admins
- **Responsive design** with modern UI

## 🔐 Authentication Flow

### 1. User Registration
```javascript
// Frontend sends registration data
const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'password123',
        first_name: 'John',
        last_name: 'Doe',
        role: 'student'
    })
});
```

### 2. User Login
```javascript
// Frontend sends login credentials
const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'password123'
    })
});

// Store user data in localStorage
localStorage.setItem('user', JSON.stringify(data.user));
```

### 3. Protected API Calls
```javascript
// All subsequent API calls include credentials
const response = await fetch('/api/dashboard/risk-data', {
    credentials: 'include'  // Important for session cookies
});
```

## 🎨 UI/UX Features

### Design System
- **Tailwind CSS** for consistent styling
- **Inter font** for modern typography
- **Color scheme**: Green primary, slate secondary
- **Responsive breakpoints** for all screen sizes

### Components
- **Navigation bars** with role-based menus
- **Form inputs** with validation states
- **Data tables** with sorting and filtering
- **Charts** using Chart.js integration
- **Chat interface** with real-time messaging

### Accessibility
- **Semantic HTML** structure
- **ARIA labels** for screen readers
- **Keyboard navigation** support
- **Color contrast** compliance

## 🔧 Technical Implementation

### JavaScript Features
- **Fetch API** for HTTP requests
- **localStorage** for client-side data persistence
- **Event listeners** for form interactions
- **Dynamic content** based on user roles
- **Error handling** with user feedback

### API Integration
- **RESTful endpoints** for all operations
- **JSON data format** for requests/responses
- **Session cookies** for authentication
- **CORS headers** for cross-origin requests

### Security
- **Input validation** on both frontend and backend
- **XSS protection** through proper escaping
- **CSRF protection** via session cookies
- **Role-based access** control

## 📊 Role-Based Features

### Student Dashboard
- **AI Chat Interface**: Real-time conversation with counselor bot
- **Personal Data**: View own wellness metrics
- **Progress Tracking**: Monitor improvement over time

### Counselor Dashboard
- **Risk Assessment Table**: View all student risk scores
- **Student Management**: Access detailed student profiles
- **Intervention Tools**: Mark students for follow-up

### Faculty Dashboard
- **Class Reports**: View aggregated class performance
- **Student Alerts**: Get notified of at-risk students
- **Analytics**: Performance trends and insights

### Admin Dashboard
- **System Statistics**: User counts, active sessions
- **User Management**: Create/edit user accounts
- **System Monitoring**: Health checks and logs

## 🚀 Deployment

### Development
```bash
# Start backend
python src/main_server.py

# Access frontend
open http://localhost:5000
```

### Production
```bash
# Use production WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 src.main_server:app
```

### Static File Serving
- **Flask static folder**: Serves HTML files directly
- **CDN ready**: Can be moved to CDN for better performance
- **Caching**: Configure appropriate cache headers

## 🔄 API Endpoints Used

| Method | Endpoint | Purpose | Frontend Usage |
|--------|----------|---------|----------------|
| POST | `/api/auth/register` | User registration | Signup form |
| POST | `/api/auth/login` | User authentication | Login form |
| POST | `/api/auth/logout` | User logout | Dashboard logout |
| GET | `/api/auth/me` | Get current user | User info display |
| POST | `/api/chatbot/chat` | AI chat | Student chat interface |
| GET | `/api/dashboard/risk-data` | Risk assessments | Counselor/faculty tables |
| GET | `/api/dashboard/students` | Student list | Admin user management |

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend CORS is configured for frontend domain
   - Check that credentials are included in requests

2. **Authentication Issues**
   - Verify session cookies are being set
   - Check localStorage for user data
   - Ensure API endpoints are protected correctly

3. **Static File Issues**
   - Verify static folder path is correct
   - Check file permissions
   - Ensure Flask is serving static files

4. **API Connection Issues**
   - Verify backend is running on correct port
   - Check network connectivity
   - Review browser console for errors

### Debug Mode
```javascript
// Enable debug logging in browser console
localStorage.setItem('debug', 'true');

// Check authentication status
console.log('User:', localStorage.getItem('user'));

// Test API connectivity
fetch('/api/health').then(r => r.json()).then(console.log);
```

## 📈 Performance Optimization

### Frontend
- **Minify CSS/JS** for production
- **Optimize images** and assets
- **Enable gzip** compression
- **Use CDN** for static assets

### Backend
- **Database indexing** for fast queries
- **API response caching** where appropriate
- **Connection pooling** for database
- **Load balancing** for high traffic

## 🔮 Future Enhancements

### Planned Features
- **Real-time notifications** using WebSockets
- **Progressive Web App** (PWA) capabilities
- **Offline support** with service workers
- **Advanced analytics** with more chart types
- **Mobile app** using the same API

### Technical Improvements
- **TypeScript** for better type safety
- **Component library** for reusable UI elements
- **State management** with Redux/Vuex
- **Testing framework** for frontend code

---

This frontend integration provides a complete, production-ready interface for the ShikshaSamvad platform while maintaining simplicity and ease of maintenance.
