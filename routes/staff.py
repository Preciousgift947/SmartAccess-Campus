from flask import Blueprint, render_template, session, jsonify, request
import mysql.connector
import bcrypt
import logging
import re
from datetime import datetime, timedelta, timezone
from functools import wraps

from config import Config
from routes.auth import role_required


staff_bp = Blueprint('staff', __name__)

STAFF_ROLES = ('Administrator', 'Security Personnel')
ADMIN_ROLES = ('Administrator',)

logger = logging.getLogger(__name__)


def get_db():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT
    )


def api_staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'}), 401
        if session.get('role') not in STAFF_ROLES:
            return jsonify({'success': False, 'message': 'Staff access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def api_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'}), 401
        if session.get('role') not in ADMIN_ROLES:
            return jsonify({'success': False, 'message': 'Administrator access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


@staff_bp.route('/reports')
@role_required(*STAFF_ROLES)
def reports():
    return render_template('reports.html')


@staff_bp.route('/api/reports')
@api_staff_required
def api_reports():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT m.Module_Code,
               m.Module_Name,
               COALESCE(CAST(COUNT(a.Attendance_ID) AS SIGNED), 0) AS total_records,
               COALESCE(CAST(SUM(a.Status = 'Present') AS SIGNED), 0) AS present,
               COALESCE(CAST(SUM(a.Status = 'Late') AS SIGNED), 0) AS late,
               COALESCE(CAST(SUM(a.Status = 'Absent') AS SIGNED), 0) AS absent
        FROM MODULE m
        LEFT JOIN ATTENDANCE a
            ON a.Module_ID = m.Module_ID
        GROUP BY m.Module_ID, m.Module_Code, m.Module_Name
        ORDER BY m.Module_Code
    ''')

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'modules': rows})


@staff_bp.route('/api/staff_profile')
@api_staff_required
def api_staff_profile():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT Admin_ID,
               First_Name,
               Last_Name,
               Email,
               Role
        FROM ADMIN
        WHERE Admin_ID = %s
    ''', (session['user_id'],))

    staff = cursor.fetchone()

    cursor.close()
    conn.close()

    if not staff:
        return jsonify({'success': False, 'message': 'Staff not found'}), 404

    return jsonify(staff)


@staff_bp.route('/api/scans')
@api_staff_required
def api_scans():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''
        SELECT a.Attendance_ID,
               s.Student_Number,
               CONCAT(s.First_Name, ' ', s.Last_Name) AS Student_Name,
               m.Module_Code,
               a.Attendance_Date,
               CAST(a.Scan_Time AS CHAR) AS Scan_Time,
               a.Status,
               a.Gate_Location
        FROM ATTENDANCE a
        JOIN STUDENT s
            ON s.Student_ID = a.Student_ID
        JOIN MODULE m
            ON m.Module_ID = a.Module_ID
        ORDER BY a.Attendance_Date DESC, a.Scan_Time DESC
        LIMIT 100
    ''')

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({'scans': rows})

@staff_bp.route('/scanner')
@role_required('Administrator', 'Security Personnel')
def scanner():
    return render_template('scanner.html')

@staff_bp.route('/verification')
@role_required('Administrator', 'Security Personnel')
def verification():
    return render_template('verification.html')


# ============================================
# ADD STUDENT (administrators only)
# ============================================

@staff_bp.route('/add-student')
@role_required(*ADMIN_ROLES)
def add_student_page():
    return render_template('add_student.html')


@staff_bp.route('/api/students', methods=['POST'])
@api_admin_required
def api_add_student():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'success': False, 'message': 'Invalid request body'}), 400

    def clean(key):
        value = data.get(key)
        return value.strip() if isinstance(value, str) else ''

    first_name = clean('first_name')
    last_name = clean('last_name')
    student_number = clean('student_number')
    email = clean('email')
    phone = clean('phone_number')
    course = clean('course')
    faculty = clean('faculty')
    password = data.get('password') if isinstance(data.get('password'), str) else ''

    # ---- validation ----
    if not all([first_name, last_name, student_number, email, course, faculty, password]):
        return jsonify({'success': False,
                        'message': 'Please fill in all required fields'}), 400

    if len(first_name) > 50 or len(last_name) > 50:
        return jsonify({'success': False,
                        'message': 'First and last name must be 50 characters or fewer'}), 400

    if not re.fullmatch(r'[A-Za-z0-9]{3,20}', student_number):
        return jsonify({'success': False,
                        'message': 'Student number must be 3 to 20 letters or digits'}), 400

    if len(email) > 100 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        return jsonify({'success': False, 'message': 'Please enter a valid email address'}), 400

    if phone and not re.fullmatch(r'[0-9+ ]{7,15}', phone):
        return jsonify({'success': False,
                        'message': 'Phone number must be 7 to 15 digits'}), 400

    if len(course) > 100 or len(faculty) > 100:
        return jsonify({'success': False,
                        'message': 'Course and faculty must be 100 characters or fewer'}), 400

    if len(password) < 8:
        return jsonify({'success': False,
                        'message': 'Password must be at least 8 characters'}), 400

    if len(password.encode('utf-8')) > 72:
        return jsonify({'success': False,
                        'message': 'Password is too long (72 characters at most)'}), 400

    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    today = datetime.now(timezone(timedelta(hours=2))).date()
    expiry = today + timedelta(days=365)

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''
            INSERT INTO STUDENT
                (First_Name, Last_Name, Student_Number, Email,
                 Phone_Number, Course, Faculty, Password_Hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (first_name, last_name, student_number, email,
             phone or None, course, faculty, password_hash)
        )
        student_id = cursor.lastrowid

        # Every student gets an Active digital access card straight away.
        # Their QR code is created when they first open Digital ID.
        cursor.execute(
            '''
            INSERT INTO DIGITAL_ACCESS_CARD
                (Student_ID, QR_Code_Data, Issue_Date, Expiry_Date, Card_Status)
            VALUES (%s, %s, %s, %s, 'Active')
            ''',
            (student_id, '', today, expiry)
        )

        conn.commit()

    except mysql.connector.IntegrityError:
        conn.rollback()
        return jsonify({'success': False,
                        'message': 'A student with that student number or email already exists'}), 409

    except mysql.connector.Error:
        conn.rollback()
        logger.exception("DB error in api_add_student")
        return jsonify({'success': False,
                        'message': 'Could not add the student. Please try again.'}), 500

    finally:
        cursor.close()
        conn.close()

    return jsonify({
        'success': True,
        'message': 'Student added',
        'student': {
            'Student_ID': student_id,
            'Name': f'{first_name} {last_name}',
            'Student_Number': student_number
        }
    }), 201
