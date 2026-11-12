from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
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
# MANAGE STUDENTS (administrators only)
# ============================================

STUDENT_COLUMNS = (
    'Student_ID, First_Name, Last_Name, Student_Number, Email, '
    'Phone_Number, Course, Faculty, Registration_Date'
)


@staff_bp.route('/students')
@role_required(*ADMIN_ROLES)
def students_page():
    return render_template('students.html')


@staff_bp.route('/add-student')
@role_required(*ADMIN_ROLES)
def add_student_page():
    # Old address: the add form now lives on the Students page
    return redirect(url_for('staff.students_page'))


def _read_student_fields(data, password_required):
    """Validate the student form. Returns (fields, None) or (None, error_response)."""
    if not isinstance(data, dict):
        return None, (jsonify({'success': False, 'message': 'Invalid request body'}), 400)

    def clean(key):
        value = data.get(key)
        return value.strip() if isinstance(value, str) else ''

    def fail(message):
        return None, (jsonify({'success': False, 'message': message}), 400)

    first_name = clean('first_name')
    last_name = clean('last_name')
    student_number = clean('student_number')
    email = clean('email')
    phone = clean('phone_number')
    course = clean('course')
    faculty = clean('faculty')
    password = data.get('password') if isinstance(data.get('password'), str) else ''

    required = [first_name, last_name, student_number, email, course, faculty]
    if password_required:
        required.append(password)
    if not all(required):
        return fail('Please fill in all required fields')

    if len(first_name) > 50 or len(last_name) > 50:
        return fail('First and last name must be 50 characters or fewer')

    if not re.fullmatch(r'[A-Za-z0-9]{3,20}', student_number):
        return fail('Student number must be 3 to 20 letters or digits')

    if len(email) > 100 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        return fail('Please enter a valid email address')

    if phone and not re.fullmatch(r'[0-9+ ]{7,15}', phone):
        return fail('Phone number must be 7 to 15 digits')

    if len(course) > 100 or len(faculty) > 100:
        return fail('Course and faculty must be 100 characters or fewer')

    password_hash = None
    if password:
        if len(password) < 8:
            return fail('Password must be at least 8 characters')
        if len(password.encode('utf-8')) > 72:
            return fail('Password is too long (72 characters at most)')
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    return {
        'first_name': first_name,
        'last_name': last_name,
        'student_number': student_number,
        'email': email,
        'phone': phone or None,
        'course': course,
        'faculty': faculty,
        'password_hash': password_hash,
    }, None


@staff_bp.route('/api/students', methods=['GET'])
@api_admin_required
def api_list_students():
    query = (request.args.get('q') or '').strip()[:100]

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        sql = f'SELECT {STUDENT_COLUMNS} FROM STUDENT'
        params = ()
        if query:
            like = f'%{query}%'
            sql += (' WHERE First_Name LIKE %s OR Last_Name LIKE %s'
                    ' OR CONCAT(First_Name, " ", Last_Name) LIKE %s'
                    ' OR Student_Number LIKE %s OR Email LIKE %s')
            params = (like, like, like, like, like)
        sql += ' ORDER BY Last_Name, First_Name LIMIT 500'

        cursor.execute(sql, params)
        rows = cursor.fetchall()

    except mysql.connector.Error:
        logger.exception("DB error in api_list_students")
        return jsonify({'success': False,
                        'message': 'Could not load students. Please try again.'}), 500

    finally:
        cursor.close()
        conn.close()

    for row in rows:
        if row.get('Registration_Date'):
            row['Registration_Date'] = row['Registration_Date'].isoformat()

    return jsonify({'success': True, 'students': rows})


@staff_bp.route('/api/students', methods=['POST'])
@api_admin_required
def api_add_student():
    fields, error = _read_student_fields(
        request.get_json(silent=True), password_required=True
    )
    if error:
        return error

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
            (fields['first_name'], fields['last_name'], fields['student_number'],
             fields['email'], fields['phone'], fields['course'],
             fields['faculty'], fields['password_hash'])
        )
        student_id = cursor.lastrowid

        # Every student gets an Active digital access card straight away.
        # Their QR code is created when they first open their QR page.
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
            'Name': f"{fields['first_name']} {fields['last_name']}",
            'Student_Number': fields['student_number']
        }
    }), 201


@staff_bp.route('/api/students/<int:student_id>', methods=['PUT'])
@api_admin_required
def api_update_student(student_id):
    # Password is optional here: leave it out to keep the current one.
    fields, error = _read_student_fields(
        request.get_json(silent=True), password_required=False
    )
    if error:
        return error

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT 1 FROM STUDENT WHERE Student_ID = %s', (student_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Student not found'}), 404

        sql = (
            'UPDATE STUDENT SET First_Name = %s, Last_Name = %s, '
            'Student_Number = %s, Email = %s, Phone_Number = %s, '
            'Course = %s, Faculty = %s'
        )
        params = [fields['first_name'], fields['last_name'],
                  fields['student_number'], fields['email'], fields['phone'],
                  fields['course'], fields['faculty']]

        if fields['password_hash']:
            sql += ', Password_Hash = %s'
            params.append(fields['password_hash'])

        sql += ' WHERE Student_ID = %s'
        params.append(student_id)

        cursor.execute(sql, tuple(params))
        conn.commit()

    except mysql.connector.IntegrityError:
        conn.rollback()
        return jsonify({'success': False,
                        'message': 'A student with that student number or email already exists'}), 409

    except mysql.connector.Error:
        conn.rollback()
        logger.exception("DB error in api_update_student")
        return jsonify({'success': False,
                        'message': 'Could not save the changes. Please try again.'}), 500

    finally:
        cursor.close()
        conn.close()

    return jsonify({
        'success': True,
        'message': 'Student updated',
        'password_changed': bool(fields['password_hash'])
    })


@staff_bp.route('/api/students/<int:student_id>', methods=['DELETE'])
@api_admin_required
def api_delete_student(student_id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'SELECT First_Name, Last_Name, Student_Number FROM STUDENT '
            'WHERE Student_ID = %s',
            (student_id,)
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Student not found'}), 404

        # The database removes their card, attendance, notifications and
        # module links automatically (ON DELETE CASCADE).
        cursor.execute('DELETE FROM STUDENT WHERE Student_ID = %s', (student_id,))
        conn.commit()

    except mysql.connector.Error:
        conn.rollback()
        logger.exception("DB error in api_delete_student")
        return jsonify({'success': False,
                        'message': 'Could not remove the student. Please try again.'}), 500

    finally:
        cursor.close()
        conn.close()

    logger.info("Student %s (%s) removed by admin %s",
                row[2], student_id, session.get('user_id'))

    return jsonify({
        'success': True,
        'message': 'Student removed',
        'student': {'Name': f'{row[0]} {row[1]}', 'Student_Number': row[2]}
    })
