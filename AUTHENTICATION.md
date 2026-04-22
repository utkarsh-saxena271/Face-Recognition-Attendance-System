# Authentication System Documentation

## Overview

The Face Recognition Attendance System includes a complete authentication system using Flask-Login. It manages user registration, login, sessions, roles, and attendance tracking.

Email notifications are handled using **EmailJS (frontend-based system)** instead of SMTP.

---

## Features

### 1. User Registration

* Self-registration with validation
* Gmail-based email field
* Password strength validation
* Role assignment (default: user)

---

### 2. User Login

* Username/password authentication
* Secure password hashing (PBKDF2-HMAC SHA256)
* Session management
* Login attempt logging

---

### 3. Session Management

* Configurable timeout (default: 30 minutes)
* Remember me functionality
* Secure cookies
* Automatic logout on timeout

---

### 4. Password Management

* Change password functionality
* Password validation rules
* Secure password storage

---

### 5. Role-Based Access Control

* User, Manager, Admin roles
* Protected routes using decorators
* Admin dashboard

---

## Authentication Flow

### Registration

1. User opens `/auth/register`
2. Fills form
3. System validates input
4. Password is hashed
5. User saved in database
6. Redirect to login

---

### Login

1. User opens `/auth/login`
2. Enters credentials
3. System validates
4. Session created
5. Redirect to dashboard

---

## User Profile

* View personal details
* Attendance summary
* Recent attendance records

---

## Email Notifications (EmailJS)

### Overview

Emails are sent using **EmailJS (JavaScript in frontend)**.

---

### How It Works

1. Attendance marked successfully
2. Browser triggers EmailJS
3. Email sent directly to user

---

### Frontend Setup

```html id="c9uvr2"
<script src="https://cdn.jsdelivr.net/npm/emailjs-com@3/dist/email.min.js"></script>

<script>
emailjs.init("YOUR_PUBLIC_KEY");

function sendEmail(name, email, date, time) {
    emailjs.send("YOUR_SERVICE_ID", "YOUR_TEMPLATE_ID", {
        name: name,
        email: email,
        date: date,
        time: time
    });
}
</script>
```

---

### Advantages

* No backend email server
* No SMTP configuration
* No password storage
* Faster integration

---

## Role-Based Access

### User

* Mark attendance
* View reports

### Manager

* View team reports

### Admin

* Manage users
* View all data
* System control

---

## Protected Routes

```python id="zsqj0k"
@login_required
/dashboard

@login_required
/camera

@role_required('admin')
/admin/*
```

---

## API Security

All `/api/*` routes require authentication:

```python id="b3c4yx"
@login_required
def mark_attendance():
    pass
```

---

## Database Schema

### Users Table

```sql id="f9j2a3"
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT,
    full_name TEXT,
    embedding BLOB,
    role TEXT,
    status TEXT
);
```

---

## Configuration

### Environment Variables

```env id="9x4kpl"
SECRET_KEY=your-secret-key
SESSION_TIMEOUT_MINUTES=30

ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=strong-password
```

👉 No SMTP required

---

## Security

### Password Security

* Hashed using PBKDF2
* Secure comparison

---

### Session Security

* HTTP-only cookies
* Secure flag (production)

---

### Best Practices

* Never store plain passwords
* Use HTTPS
* Validate inputs

---

## Logging

Logs stored in:

```id="lb1h7x"
logs/
```

---

## Integration

### Face Recognition

* Works only for logged-in user
* Face linked with user ID

---

### EmailJS Integration

* Triggered after attendance
* Sends confirmation email
* Runs on frontend

---

## Troubleshooting

### Login Issues

* Check username/password
* Check account status

---

### Email Not Working

* Verify EmailJS public key
* Check service & template ID
* Check browser console (F12)

---

### Session Issues

* Check timeout settings
* Enable cookies in browser

---

## Future Enhancements

* Email verification
* Password reset
* Two-factor authentication
* OAuth login (Google)

---

## Summary

* Authentication handled by Flask-Login
* Email handled by EmailJS
* No backend email server needed
* Clean and deployment-ready system
