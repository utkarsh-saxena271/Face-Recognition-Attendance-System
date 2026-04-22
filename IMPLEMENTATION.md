# Authentication System Implementation Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key packages:

* Flask
* Flask-Login
* Flask-WTF
* WTForms
* APScheduler
* numpy, opencv, face-recognition

---

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
SESSION_TIMEOUT_MINUTES=30

ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=SecurePassword123!
```

👉 No SMTP required

---

### 3. Run Application

```bash
python run.py
```

Open:

```
http://localhost:5000
```

---

## Email Notifications (EmailJS)

### Overview

This project uses **EmailJS (frontend-based email system)** instead of SMTP.

---

### How It Works

1. User marks attendance
2. Face is recognized
3. Attendance saved in database
4. Email is sent using **EmailJS (JavaScript)**

---

### Setup EmailJS

1. Go to: https://www.emailjs.com/
2. Create account
3. Create:

   * Email Service (Gmail or others)
   * Email Template
4. Get:

   * Public Key
   * Service ID
   * Template ID

---

### Add in Frontend

```html
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

### Advantages of EmailJS

* No backend email setup
* No SMTP configuration
* No password storage
* Easy integration

---

## Authentication Features

### User Registration

* Full name
* Username
* Gmail validation
* Password validation

### User Login

* Username/password
* Session management
* Remember me

### Role-Based Access

* User
* Manager
* Admin

---

## Attendance System

### Flow

1. Open camera
2. Capture image
3. Send to backend
4. Recognize face
5. Mark attendance
6. Send email via EmailJS

---

## API Example

### Recognize Face

```json
POST /api/recognize-face

{
  "image": "base64-image"
}
```

Response:

```json
{
  "success": true,
  "found": true,
  "user_name": "John Doe",
  "status": "present"
}
```

---

## Scheduler

* Marks absent users automatically
* Generates reports
* Runs background tasks

---

## Logging

Logs stored in:

```
logs/
```

---

## Troubleshooting

### Email not working

* Check EmailJS public key
* Check service ID & template ID
* Open browser console (F12)

---

### Login issues

* Check username/password
* Ensure account is active

---

### Camera issues

* Allow browser camera permission
* Use HTTPS in production

---

## Deployment Notes

* Do NOT upload `.env`
* Do NOT upload `venv/`
* Use `requirements.txt`

---

## Future Improvements

* Email verification
* Password reset
* 2FA authentication
* Cloud deployment
