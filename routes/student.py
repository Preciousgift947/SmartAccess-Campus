from flask import Blueprint, render_template, redirect, url_for, session, abort, jsonify
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

        if session.get('role') != 'student':
            abort(403)

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
    conn = None
    cursor = None

    try:
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

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None:
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
    conn = None
    cursor = None

    try:
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
            ORDER BY dac.Issue_Date DESC
            LIMIT 1
        ''', (session['student_id'],))

        student = cursor.fetchone()

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()

    return render_template(
        'digital_id.html',
        student=student
    )
    # ============================================
# STUDENT PROFILE PAGE
# ============================================

@student_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# ============================================
# STUDENT PROFILE API
# ============================================

@student_bp.route('/api/profile', methods=['GET'])
@login_required
def profile_api():
    conn = None
    cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT
                Student_Number,
                First_Name,
                Last_Name,
                Email,
                Course,
                Faculty,
                Photo_URL
            FROM STUDENT
            WHERE Student_ID = %s
        ''', (session['student_id'],))

        profile = cursor.fetchone()

        if profile is None:
            return jsonify({
                'message': 'Student profile not found.'
            }), 404

        return jsonify({
            'profile': profile
        }), 200

    except mysql.connector.Error:
        return jsonify({
            'message': 'Could not load student profile.'
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()



# ============================================
# ATTENDANCE
# ============================================


@student_bp.route('/attendance')
@login_required
def attendance():
    conn = None
    cursor = None

    try:
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

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None:
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
    conn = None
    cursor = None

    try:
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

        # Mark only this student's notifications as read
        cursor.execute(
            'UPDATE NOTIFICATION '
            'SET Is_Read = TRUE '
            'WHERE Student_ID = %s',
            (session['student_id'],)
        )

        conn.commit()

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()

    return render_template(
        'notifications.html',
        notifications=notifications
    )
# ============================================
# STUDENT ACADEMIC CALENDAR
# ============================================

@student_bp.route('/student/calendar')
@login_required
def calendar():
    return render_template('academic_calendar.html')

# ============================================
# STUDENT ACADEMIC CALENDAR API
# ============================================

@student_bp.route('/api/calendar')
@login_required
def calendar_events():

    conn = None
    cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT DISTINCT
                ae.Event_ID,
                ae.Event_Type,
                ae.Event_Date,
                ae.Event_Description,
                ae.Reminder_Date,
                m.Module_Code,
                m.Module_Name
            FROM STUDENT_MODULE sm
            INNER JOIN ACADEMIC_EVENT ae
                ON sm.Module_ID = ae.Module_ID
            INNER JOIN MODULE m
                ON ae.Module_ID = m.Module_ID
            WHERE sm.Student_ID = %s
            ORDER BY ae.Event_Date ASC
        ''', (session['student_id'],))

        events = cursor.fetchall()

        for event in events:
            event['Event_Date'] = event['Event_Date'].isoformat()
            event['Reminder_Date'] = event['Reminder_Date'].isoformat()

        return jsonify({
            'status': 'success',
            'events': events
        }), 200

    except mysql.connector.Error:
        return jsonify({
            'status': 'error',
            'message': 'Could not load academic events.'
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()
