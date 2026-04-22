# Face Recognition Attendance System

A light-weight, modular, web-based Face Recognition Attendance System built with Python, Flask, OpenCV, FaceNet, and Vanilla JS.

## Features
- **Browser-based Camera Integration**: Access the webcam directly from the web browser without any desktop GUI popups.
- **Real-time Face Tracking**: Generate facial embeddings upon capture and automatically attempt to match the logged face.
- **Attendance Logging System**: Captures time constraints (blocks duplicate attendances on the same day).
- **Zero Heavy Frameworks**: Front-end uses pure semantic HTML5, custom CSS, and Vanilla JS `fetch()` capabilities. 
- **Lightweight DB**: Employs SQLite string-stored array vector capabilities for fast setup.

---

## Folder Structure

```
├── app/
│   ├── __init__.py           # Flask App Factory setup
│   ├── models/
│   │   └── db.py             # SQLite helper methods for attendance & users
│   ├── routes/
│   │   ├── api.py            # API REST endpoints (Recognize & Register)
│   │   └── views.py          # HTML Template endpoints
│   ├── services/
│   │   └── face_service.py   # OpenCV & FaceNet embedded logic
│   ├── utils/
│   │   └── helpers.py        # Base64 to cv2 parsers and image manipulation
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Clean visual styles
│   │   └── js/
│   │       └── main.js       # Face captures bounding box and API requests
│   └── templates/            # HTML Views mapping 
├── venv/                     # Python Virtual Environment
├── database.db               # Auto-generated embedded Database
├── requirements.txt          # Python Package Requirements 
├── run.py                    # Entrypoint Execution
└── start.md                  # Detailed Developer documentation
```

---

## Local Setup & Installation

### 1. Prerequisites
- **Python 3.8+**
- (Mac users) Ensure Xcode CLI Tools or `cmake` are installed since we compile `dlib` automatically to install `face_recognition`.

### 2. Setup Virtual Environment (Recommended)

Move into the project directory and create a new Python virtual environment to house your dependencies cleanly:

```bash
# Create Virtual Environment
python3 -m venv venv

# Activate Environment (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

Install the listed project libraries (Flask, OpenCV, Numpy, Face_recognition):

```bash
pip install -r requirements.txt
```

### 4. Run the Server

Once installed, simply start the server by executing the `run.py` script:

```bash
python run.py
```

*By default, the server spins up automatically at `http://127.0.0.1:5000`.*

---

## How to Test Features

1. **Dashboard:** Start by accessing `http://127.0.0.1:5000` in your browser.
2. **Register a Face:** Click "Register New User". Fill in the form and look directly at your webcam when hitting the `Capture & Register` button. This generates and saves your vector to the SQLite `database.db`.
3. **Capture Attendance:** Navigate to "Take Attendance" (`/camera`). The moment you activate the 'Scan Face' scanner, it will map your frame to your encoded profile and immediately push an attendance record.
4. **View Logs:** Review all attendances in the "Reports" (`/report`) tab dynamically.
