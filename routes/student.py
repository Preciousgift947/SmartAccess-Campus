from flask import Blueprint, render_template, redirect, url_for, session
import mysql.connector
from config import Config

student_bp = Blueprint('student', __name__)


def get_db():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT
    )


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated_function


# ============================================
# HOME - Redirect to Dashboard
# ============================================

@student_bp.route('/')
@login_required
def home():
    if 'student_id' in session:
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))

# ============================================
# DASHBOARD
# ============================================

@student_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Get Digital ID / Access Card status
    cursor.execute(
        'SELECT * FROM DIGITAL_ACCESS_CARD WHERE Student_ID = %s',
        (session['student_id'],)
    )

    card = cursor.fetchone()

    # Get unread notifications count
    cursor.execute(
        'SELECT COUNT(*) AS count '
        'FROM NOTIFICATION '
        'WHERE Student_ID = %s AND Is_Read = FALSE',
        (session['student_id'],)
    )

    unread = cursor.fetchone()['count']

    cursor.close()
    conn.close()

    return render_template(
        'dashboard.html',
        card=card,
        unread_notifications=unread,
        student_name=session['student_name'],
        course=session['course']
    )


# ============================================
# DIGITAL ID
# ============================================

@student_bp.route('/digital_id')
@login_required
def digital_id():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT s.*,
               dac.Card_Status,
               dac.Expiry_Date,
               dac.Issue_Date,
               dac.QR_Code_Data
        FROM STUDENT s
        JOIN DIGITAL_ACCESS_CARD dac
            ON s.Student_ID = dac.Student_ID
        WHERE s.Student_ID = %s
    ''', (session['student_id'],))

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'digital_id.html',
        student=student
    )


# ============================================
# ATTENDANCE
# ============================================

@student_bp.route('/attendance')
@login_required
def attendance():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT a.Attendance_ID,
               a.Attendance_Date,
               a.Status,
               a.Scan_Time,
               a.Gate_Location,
               m.Module_Name,
               m.Module_Code
        FROM ATTENDANCE a
        JOIN MODULE m
            ON a.Module_ID = m.Module_ID
        WHERE a.Student_ID = %s
        ORDER BY a.Attendance_Date DESC, a.Scan_Time DESC
    ''', (session['student_id'],))

    attendance_records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'attendance.html',
        attendance_records=attendance_records
    )


# ============================================
# NOTIFICATIONS
# ============================================

@student_bp.route('/notifications')
@login_required
def notifications():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT n.Notification_ID,
               n.Message,
               n.Sent_Date,
               n.Is_Read,
               ae.Event_Type,
               ae.Event_Date
        FROM NOTIFICATION n
        LEFT JOIN ACADEMIC_EVENT ae
            ON n.Event_ID = ae.Event_ID
        WHERE n.Student_ID = %s
        ORDER BY n.Sent_Date DESC
    ''', (session['student_id'],))

    notifications = cursor.fetchall()

    # Mark notifications as read
    cursor.execute(
        'UPDATE NOTIFICATION '
        'SET Is_Read = TRUE '
        'WHERE Student_ID = %s',
        (session['student_id'],)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return render_template(
        'notifications.html',
        notifications=notifications
    )