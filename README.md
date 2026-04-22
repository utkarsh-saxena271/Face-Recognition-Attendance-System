# 📄 Software Requirements Specification (SRS)

## 1. Introduction

### 1.1 Purpose

The purpose of this system is to automate attendance management using face recognition technology. It eliminates manual attendance processes and prevents proxy attendance by verifying user identity through facial features.

---

### 1.2 Scope

The system provides:

* User registration and authentication
* Face data capture and encoding
* Real-time attendance marking using webcam
* Admin dashboard for monitoring
* Attendance report generation
* Email notification support

This is a web-based application built using Flask and computer vision libraries.

---

### 1.3 Definitions

* **User**: Individual marking attendance
* **Admin**: System manager with elevated privileges
* **Face Encoding**: Numerical representation of facial features
* **Attendance Record**: Stored entry of user presence with timestamp

---

## 2. Overall Description

### 2.1 Product Perspective

The system is a full-stack web application integrating:

* Frontend interface (HTML, CSS, JavaScript)
* Backend server (Flask)
* Face recognition engine (OpenCV, face_recognition)
* Database system (SQLite - current, PostgreSQL - recommended)

---

### 2.2 System Architecture

```
User → Webcam Capture → Face Encoding → Match with Database → Mark Attendance → Store Record → Display Report
```

---

### 2.3 User Classes

#### User

* Register and login
* Capture facial data
* Mark attendance
* View attendance records

#### Admin

* Manage users
* Monitor attendance
* Generate reports

---

### 2.4 Operating Environment

* Web browser (Chrome recommended)
* Backend server (Flask)
* Deployment platforms (Docker, Render)

---

## 3. Functional Requirements

### 3.1 Authentication System

* Users can register and login securely
* Session management is maintained
* Only authenticated users can access system features

---

### 3.2 Face Registration

* System captures user face via webcam
* Generates face encoding
* Stores encoding in database

---

### 3.3 Face Recognition Attendance

* Detects face in real-time
* Matches with stored encodings
* Marks attendance if matched

---

### 3.4 Attendance Management

* Stores attendance with date and time
* Prevents duplicate entries for the same day

---

### 3.5 Admin Dashboard

* View all users
* View attendance records
* Filter/search data

---

### 3.6 Reporting System

* Generate attendance reports
* Display data in UI
* (Future) Export functionality

---

### 3.7 Email Notification

* Send attendance reports via email
* Scheduled notifications

---

## 4. System Workflow

1. User registers and captures face data
2. User logs into the system
3. User opens camera interface
4. System detects and verifies face
5. Attendance is marked automatically
6. Data is stored in database
7. Admin monitors via dashboard

---

## 5. Data Requirements

### Users Table

* id
* name
* email
* password

### Face Encodings

* user_id
* encoding data

### Attendance Table

* user_id
* date
* time
* status

---

## 6. Non-Functional Requirements

### Security

* Password hashing
* Session-based authentication
* (Future) JWT-based authentication

---

### Performance

* Real-time face recognition
* Efficient database operations

---

### Scalability

* Current: SQLite (local use)
* Future: PostgreSQL (production-ready)

---

### Usability

* Simple and intuitive interface
* Easy navigation

---

### Reliability

* Accurate face detection
* Error handling for failures

---

## 7. Limitations

* Performance depends on lighting conditions
* Webcam access may not work on all cloud platforms
* SQLite is not suitable for large-scale deployment
* No liveness detection (risk of spoofing)

---

## 8. Future Enhancements

* JWT Authentication
* Cloud-based face recognition
* Mobile application support
* Role-based access control
* Liveness detection (anti-spoofing)
* Advanced analytics dashboard

---

## 9. Module Mapping

| Module           | File                      |
| ---------------- | ------------------------- |
| Authentication   | routes/auth.py            |
| API              | routes/api.py             |
| Views            | routes/views.py           |
| Face Recognition | services/face_service.py  |
| Email Service    | services/email_service.py |
| Scheduler        | services/scheduler.py     |
| Database         | models/db.py              |

---
