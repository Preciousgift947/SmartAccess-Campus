from flask import Blueprint, render_template, session, jsonify
import mysql.connector
from functools import wraps

from config import Config
from routes.auth import role_required


staff_bp = Blueprint('staff', __name__)

STAFF_ROLES = ('Administrator', 'Security Personnel')


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
