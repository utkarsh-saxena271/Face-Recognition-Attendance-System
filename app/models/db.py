import sqlite3
from datetime import datetime, timezone, timedelta
import json
import os
from hashlib import pbkdf2_hmac

# ✅ IST TIMEZONE (ADD THIS)
IST = timezone(timedelta(hours=5, minutes=30))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'attendance_system.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def hash_password(password):
    """Hash password using PBKDF2"""
    salt = b'attendance_system_salt_2024'
    return pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000).hex()

def verify_password(password_hash, password):
    """Verify password against hash"""
    return password_hash == hash_password(password)

def init_db():
    """Initialize database with all tables"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table with authentication
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            embedding BLOB,
            role TEXT DEFAULT 'user' CHECK(role IN ('admin', 'user', 'manager')),
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
            is_verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for users table
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
    
    # Attendance table with status and detailed tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time_in TEXT,
            time_out TEXT,
            status TEXT DEFAULT 'present' CHECK(status IN ('present', 'late', 'absent', 'half_day')),
            notes TEXT,
            marked_by TEXT DEFAULT 'face_recognition',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, date)
        )
    ''')
    
    # Create indexes for attendance table
    c.execute('CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_attendance_user_id ON attendance(user_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status)')
    
    # Working hours configuration
    c.execute('''
        CREATE TABLE IF NOT EXISTS working_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week INTEGER,
            start_time TEXT,
            end_time TEXT,
            is_working_day INTEGER DEFAULT 1
        )
    ''')
    
    # Set default working hours (Monday-Friday, 9 AM - 5 PM)
    for day in range(5):  # 0-4 = Monday-Friday
        c.execute('''
            INSERT OR IGNORE INTO working_hours (day_of_week, start_time, end_time, is_working_day)
            VALUES (?, '09:00:00', '17:00:00', 1)
        ''', (day,))
    
    # Weekend (Saturday=5, Sunday=6)
    for day in [5, 6]:
        c.execute('''
            INSERT OR IGNORE INTO working_hours (day_of_week, start_time, end_time, is_working_day)
            VALUES (?, '00:00:00', '00:00:00', 0)
        ''', (day,))
    
    # Attendance reports table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_type TEXT CHECK(report_type IN ('daily', 'weekly', 'monthly')),
            report_date TEXT NOT NULL,
            total_present INTEGER DEFAULT 0,
            total_absent INTEGER DEFAULT 0,
            total_late INTEGER DEFAULT 0,
            total_half_day INTEGER DEFAULT 0,
            report_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create index for reports table
    c.execute('CREATE INDEX IF NOT EXISTS idx_reports_date ON attendance_reports(report_date)')
    
    # Email notifications log
    c.execute('''
        CREATE TABLE IF NOT EXISTS email_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email_type TEXT CHECK(email_type IN ('attendance_marked', 'absent_notification', 'daily_summary', 'weekly_summary')),
            recipient_email TEXT NOT NULL,
            subject TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'sent', 'failed')),
            error_message TEXT,
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for email notifications
    c.execute('CREATE INDEX IF NOT EXISTS idx_emails_status ON email_notifications(status)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_emails_type ON email_notifications(email_type)')
    
    # Audit log for tracking actions
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id INTEGER,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for audit logs
    c.execute('CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# ============================================
# USER MANAGEMENT
# ============================================

def create_user(username, email, password, full_name, role='user'):
    """Create a new user"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        password_hash = hash_password(password)
        c.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, role))
        
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError as e:
        if 'username' in str(e):
            return None, 'Username already exists'
        elif 'email' in str(e):
            return None, 'Email already registered'
        return None, str(e)

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    user = get_user_by_username(username)
    if not user:
        return None
    if verify_password(user['password_hash'], password):
        return user
    return None

def update_user_embedding(user_id, embedding_vector):
    """Update user's face embedding"""
    embedding_str = json.dumps(embedding_vector.tolist())
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET embedding = ? WHERE id = ?', (embedding_str, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    """Get all active users"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, username, email, full_name, role, embedding FROM users WHERE status = "active"')
    cols = [desc[0] for desc in c.description]
    users = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return users

def get_all_users_admin():
    """Get all users for administrator management."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, username, email, full_name, role, status, is_verified, created_at, updated_at
        FROM users
        ORDER BY created_at DESC, id DESC
    ''')
    cols = [desc[0] for desc in c.description]
    users = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return users

def ensure_default_admin():
    """Create the default administrator account from environment variables if needed."""
    admin_username = os.getenv('ADMIN_USERNAME', 'admin').strip()
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@gmail.com').strip().lower()
    admin_password = os.getenv('ADMIN_PASSWORD', 'Admin12345')
    admin_full_name = os.getenv('ADMIN_FULL_NAME', 'System Administrator').strip()

    existing_admin = get_user_by_username(admin_username)
    if existing_admin:
        if existing_admin.get('role') != 'admin':
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''
                UPDATE users
                SET role = 'admin', status = 'active', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (existing_admin['id'],))
            conn.commit()
            conn.close()
        return

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (username, email, password_hash, full_name, role, status, is_verified)
        VALUES (?, ?, ?, ?, 'admin', 'active', 1)
    ''', (admin_username, admin_email, hash_password(admin_password), admin_full_name))
    conn.commit()
    conn.close()

# ============================================
# ATTENDANCE MANAGEMENT
# ============================================

def _normalize_attendance_datetime(attendance_date=None, attendance_time=None):
    """Normalize attendance inputs to a timezone-aware UTC datetime plus date/time strings."""
    if attendance_date is None:
        normalized_datetime = datetime.now(IST)
    elif isinstance(attendance_date, datetime):
        normalized_datetime = attendance_date.astimezone(IST)
    elif attendance_time:
        normalized_datetime = datetime.strptime(
            f'{attendance_date} {attendance_time}', '%Y-%m-%d %H:%M:%S'
        ).replace(tzinfo=IST)
    else:
        normalized_datetime = datetime.strptime(attendance_date, '%Y-%m-%d').replace(tzinfo=IST)

    return (
        normalized_datetime,
        normalized_datetime.strftime('%Y-%m-%d'),
        normalized_datetime.strftime('%H:%M:%S')
    )


def get_latest_attendance_for_user(user_id):
    """Get the latest attendance row for a user based on stored date/time."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT *
        FROM attendance
        WHERE user_id = ?
        ORDER BY date DESC, time_in DESC, created_at DESC
        LIMIT 1
    ''', (user_id,))
    record = c.fetchone()
    conn.close()
    return dict(record) if record else None


def mark_attendance(user_id, attendance_date=None, attendance_time=None, status='present'):
    """Mark attendance for a user"""
    normalized_datetime, attendance_date, attendance_time = _normalize_attendance_datetime(
        attendance_date, attendance_time
    )
    
    conn = get_db_connection()
    c = conn.cursor()

    latest_record = get_latest_attendance_for_user(user_id)
    if latest_record and latest_record.get('time_in'):
        latest_datetime, _, _ = _normalize_attendance_datetime(
            latest_record['date'], latest_record['time_in']
        )
        time_since_last_mark = normalized_datetime - latest_datetime
        if time_since_last_mark < timedelta(hours=24):
            next_allowed_at = latest_datetime + timedelta(hours=24)
            conn.close()
            return False, next_allowed_at.isoformat()

    c.execute('SELECT id FROM attendance WHERE user_id = ? AND date = ?', (user_id, attendance_date))
    existing = c.fetchone()

    if existing:
        conn.close()
        return False, normalized_datetime.isoformat()
    else:
        # Create new record
        c.execute('''
            INSERT INTO attendance (user_id, date, time_in, status)
            VALUES (?, ?, ?, ?)
        ''', (user_id, attendance_date, attendance_time, status))
        conn.commit()
        conn.close()
        return True, 'Attendance marked'

def get_attendance_by_user(user_id, limit=50):
    """Get attendance records for a user"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT a.*, u.username, u.email, u.full_name
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        WHERE a.user_id = ?
        ORDER BY a.date DESC
        LIMIT ?
    ''', (user_id, limit))
    
    cols = [desc[0] for desc in c.description]
    records = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return records

def get_attendance_records(start_date=None, end_date=None):
    """Get all attendance records with optional date filter"""
    conn = get_db_connection()
    c = conn.cursor()
    
    if start_date and end_date:
        c.execute('''
            SELECT a.*, u.username, u.email, u.full_name
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE a.date BETWEEN ? AND ?
            ORDER BY a.date DESC, a.time_in DESC
        ''', (start_date, end_date))
    else:
        c.execute('''
            SELECT a.*, u.username, u.email, u.full_name
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.date DESC, a.time_in DESC
        ''')
    
    cols = [desc[0] for desc in c.description]
    records = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return records

def get_all_attendance_admin(limit=500):
    """Get all attendance records for administrator views."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT a.*, u.username, u.email, u.full_name, u.role
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.date DESC, a.time_in DESC, a.created_at DESC
        LIMIT ?
    ''', (limit,))
    cols = [desc[0] for desc in c.description]
    records = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return records

def get_attendance_today():
    """Get today's attendance records"""
    today = datetime.now(IST).strftime('%Y-%m-%d')
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT a.*, u.username, u.email, u.full_name
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        WHERE a.date = ?
        ORDER BY a.time_in DESC
    ''', (today,))
    
    cols = [desc[0] for desc in c.description]
    records = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return records

def check_and_mark_absent(user_id, date):
    """Mark user as absent if not marked by end of day"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if already marked
    c.execute('SELECT id FROM attendance WHERE user_id = ? AND date = ?', (user_id, date))
    existing = c.fetchone()
    
    if not existing:
        c.execute('''
            INSERT INTO attendance (user_id, date, status)
            VALUES (?, ?, 'absent')
        ''', (user_id, date))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

# ============================================
# REPORTING
# ============================================

def generate_daily_report(user_id, report_date):
    """Generate daily attendance report"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT COUNT(*) as total_present
        FROM attendance
        WHERE user_id = ? AND date = ? AND status = 'present'
    ''', (user_id, report_date))
    present = c.fetchone()['total_present']
    
    c.execute('''
        SELECT COUNT(*) as total_late
        FROM attendance
        WHERE user_id = ? AND date = ? AND status = 'late'
    ''', (user_id, report_date))
    late = c.fetchone()['total_late']
    
    report_data = {
        'user_id': user_id,
        'date': report_date,
        'present': present,
        'late': late,
        'absent': 1 - (present or late),
        'generated_at': datetime.now(IST).isoformat()
    }
    
    c.execute('''
        INSERT OR REPLACE INTO attendance_reports 
        (user_id, report_type, report_date, total_present, total_late, report_data)
        VALUES (?, 'daily', ?, ?, ?, ?)
    ''', (user_id, report_date, present, late, json.dumps(report_data)))
    
    conn.commit()
    conn.close()
    return report_data

def get_user_monthly_summary(user_id, year, month):
    """Get user's monthly attendance summary"""
    conn = get_db_connection()
    c = conn.cursor()
    
    date_pattern = f'{year:04d}-{month:02d}-%'
    
    c.execute('''
        SELECT 
            COUNT(CASE WHEN status = 'present' THEN 1 END) as total_present,
            COUNT(CASE WHEN status = 'late' THEN 1 END) as total_late,
            COUNT(CASE WHEN status = 'absent' THEN 1 END) as total_absent,
            COUNT(*) as total_days
        FROM attendance
        WHERE user_id = ? AND date LIKE ?
    ''', (user_id, date_pattern))
    
    result = c.fetchone()
    conn.close()
    
    return {
        'user_id': user_id,
        'year': year,
        'month': month,
        'present': result['total_present'] if result else 0,
        'late': result['total_late'] if result else 0,
        'absent': result['total_absent'] if result else 0,
        'total_days': result['total_days'] if result else 0
    }

# ============================================
# AUDIT LOGGING
# ============================================

def log_audit(user_id, action, resource_type=None, resource_id=None, details=None, ip_address=None):
    """Log user actions for audit trail"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, action, resource_type, resource_id, details, ip_address))
    conn.commit()
    conn.close()

# ============================================
# EMAIL NOTIFICATION TRACKING
# ============================================

def log_email_notification(user_id, email_type, recipient_email, subject):
    """Log email notification attempt"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO email_notifications (user_id, email_type, recipient_email, subject)
        VALUES (?, ?, ?, ?)
    ''', (user_id, email_type, recipient_email, subject))
    
    notification_id = c.lastrowid
    conn.commit()
    conn.close()
    return notification_id

def update_email_notification_status(notification_id, status, error_message=None):
    """Update email notification status"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE email_notifications
        SET status = ?, error_message = ?, sent_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, error_message, notification_id))
    conn.commit()
    conn.close()

def get_pending_emails():
    """Get pending email notifications"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM email_notifications
        WHERE status = 'pending'
        ORDER BY created_at ASC
    ''')
    
    cols = [desc[0] for desc in c.description]
    records = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return records

def update_user_password(user_id, new_password):
    """Update user password"""
    password_hash = hash_password(new_password)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE users
        SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (password_hash, user_id))
    conn.commit()
    conn.close()
    return c.rowcount > 0

