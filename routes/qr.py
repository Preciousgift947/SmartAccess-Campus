"""
QR generation and verification routes for SmartAccess Campus.

Endpoints:
  GET  /api/qr/generate  - student fetches their own QR (session required)
  POST /api/qr/verify    - staff-only: security verifies a scanned QR
  GET  /api/qr/status    - student fetches their card status

Token security: the UUID in the QR payload is stored on the card row at
generation time. /verify rejects any token that doesn't match the stored
value - this prevents forged or replayed tokens from granting access.
"""
import logging
from datetime import datetime, timedelta, timezone

import mysql.connector
from flask import Blueprint, jsonify, render_template, request, session

from config import Config
from routes.staff import api_staff_required
from utils.qr_utils import generate_base64_qr, decode_qr_token


qr_bp = Blueprint('qr', __name__, url_prefix='/api/qr')

# Public page a phone opens after scanning a student's QR code
qr_page_bp = Blueprint('qr_page', __name__)

logger = logging.getLogger(__name__)

TOKEN_TTL_HOURS = 24

# South African Standard Time (SAST = UTC+2, no DST)
SAST = timezone(timedelta(hours=2))


def get_db():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT
    )


def _now_sast():
    return datetime.now(SAST).replace(tzinfo=None)


# ============================================
# GENERATE QR  (student only, session-based)
# ============================================

@qr_bp.route('/generate', methods=['GET'])
def generate_qr():
    if session.get('role') != 'student':
        return jsonify({"message": "Student login required"}), 401

    student_id = session.get('student_id')
    if not student_id:
        return jsonify({"message": "Session missing student_id"}), 401

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            'SELECT Student_Number FROM STUDENT WHERE Student_ID = %s',
            (student_id,)
        )
        student = cursor.fetchone()

        if not student:
            return jsonify({"message": "Student not found"}), 404

        # Existing card of ANY status
        cursor.execute(
            '''
            SELECT Card_ID, Expiry_Date, Card_Status
            FROM DIGITAL_ACCESS_CARD
            WHERE Student_ID = %s
            ORDER BY Card_ID DESC
            LIMIT 1
            ''',
            (student_id,)
        )
        card = cursor.fetchone()

        today = _now_sast().date()
        new_expiry = today + timedelta(days=365)

        if card:
            if card['Card_Status'] in ('Suspended', 'Revoked'):
                return jsonify({
                    "message": f"Your access card is {card['Card_Status'].lower()}. "
                               f"Please contact administration."
                }), 403

            cursor.execute(
                '''
                UPDATE DIGITAL_ACCESS_CARD
                SET Card_Status = 'Active',
                    Issue_Date = %s,
                    Expiry_Date = %s
                WHERE Card_ID = %s
                ''',
                (today, new_expiry, card['Card_ID'])
            )
            card_id = card['Card_ID']
        else:
            cursor.execute(
                '''
                INSERT INTO DIGITAL_ACCESS_CARD
                    (Student_ID, QR_Code_Data, Issue_Date, Expiry_Date, Card_Status)
                VALUES (%s, %s, %s, %s, 'Active')
                ''',
                (student_id, '', today, new_expiry)
            )
            card_id = cursor.lastrowid

        base_url = (Config.PUBLIC_BASE_URL or request.host_url).rstrip('/')
        qr_result = generate_base64_qr(
            student_id, student['Student_Number'], base_url
        )

        cursor.execute(
            '''
            UPDATE DIGITAL_ACCESS_CARD
            SET QR_Token = %s,
                Token_Issued_At = %s,
                QR_Code_Data = %s
            WHERE Card_ID = %s
            ''',
            (qr_result['uuid'], _now_sast(), qr_result['token'], card_id)
        )
        conn.commit()

        return jsonify({
            "message": "QR code generated",
            "qr": {
                "image": qr_result['image'],
                "token": qr_result['token'],
            }
        }), 200

    except mysql.connector.Error:
        conn.rollback()
        logger.exception("DB error in generate_qr")
        return jsonify({"message": "Could not generate QR. Please try again."}), 500
    finally:
        cursor.close()
        conn.close()


# ============================================
# SHARED CHECK: is this QR token valid right now?
# ============================================

def _validate_card(conn, cursor, student_id, token_uuid):
    """Returns (card_row, None) when valid, else (None, (message, http_code))."""
    cursor.execute(
        '''
        SELECT c.Card_ID,
               c.QR_Token,
               c.Token_Issued_At,
               c.Expiry_Date,
               c.Card_Status,
               s.Student_Number,
               s.First_Name,
               s.Last_Name,
               s.Email,
               s.Course,
               s.Faculty
        FROM DIGITAL_ACCESS_CARD c
        JOIN STUDENT s ON s.Student_ID = c.Student_ID
        WHERE c.Student_ID = %s AND c.Card_Status = 'Active'
        ORDER BY c.Expiry_Date DESC
        LIMIT 1
        ''',
        (student_id,)
    )
    row = cursor.fetchone()

    if not row:
        return None, ("No active card found", 403)

    # TOKEN VALIDATION
    if not row['QR_Token'] or row['QR_Token'] != token_uuid:
        return None, ("Invalid or revoked QR token", 401)

    # CARD EXPIRY
    today = _now_sast().date()
    if row['Expiry_Date'] < today:
        cursor.execute(
            "UPDATE DIGITAL_ACCESS_CARD SET Card_Status = 'Expired' WHERE Card_ID = %s",
            (row['Card_ID'],)
        )
        conn.commit()
        return None, ("Card expired", 403)

    # TOKEN TTL
    if TOKEN_TTL_HOURS > 0 and row['Token_Issued_At']:
        age = _now_sast() - row['Token_Issued_At']
        if age > timedelta(hours=TOKEN_TTL_HOURS):
            return None, ("QR token expired, please regenerate", 401)

    return row, None


# ============================================
# VERIFY QR  (staff only - security scanner calls it)
# ============================================

@qr_bp.route('/verify', methods=['POST'])
@api_staff_required
def verify_qr():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid request body"}), 400

    qr_token = data.get('qr_data')
    if not qr_token or not isinstance(qr_token, str):
        return jsonify({"message": "No QR data provided"}), 400

    parsed = decode_qr_token(qr_token)
    if not parsed or 'student_id' not in parsed or 'token' not in parsed:
        return jsonify({"message": "Invalid QR code format"}), 400

    student_id = parsed['student_id']
    token_uuid = parsed['token']

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        row, error = _validate_card(conn, cursor, student_id, token_uuid)
        if error:
            return jsonify({"message": error[0]}), error[1]

        today = _now_sast().date()

        # Get first enrolled module for module display
        cursor.execute(
            '''
            SELECT m.Module_ID, m.Module_Code, m.Module_Name, m.Venue, m.Day,
                   CAST(m.Time AS CHAR) AS Module_Time
            FROM STUDENT_MODULE sm
            JOIN MODULE m ON m.Module_ID = sm.Module_ID
            WHERE sm.Student_ID = %s
            ORDER BY m.Module_ID
            LIMIT 1
            ''',
            (student_id,)
        )
        module_row = cursor.fetchone()
        module_id = module_row['Module_ID'] if module_row else None

        attendance_status = "Recorded"

        if module_id:
            # DUPLICATE CHECK: already scanned today for this module?
            cursor.execute(
                '''
                SELECT Attendance_ID FROM ATTENDANCE
                WHERE Student_ID = %s AND Module_ID = %s AND Attendance_Date = %s
                LIMIT 1
                ''',
                (student_id, module_id, today)
            )
            existing = cursor.fetchone()

            if existing:
                attendance_status = "Already recorded today"
            else:
                now = _now_sast()
                cursor.execute(
                    '''
                    INSERT INTO ATTENDANCE
                        (Student_ID, Module_ID, Attendance_Date, Status, Scan_Time, Gate_Location)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ''',
                    (
                        student_id,
                        module_id,
                        now.date(),
                        'Present',
                        now.time(),
                        data.get('gate_location') or 'Main Entrance'
                    )
                )
                conn.commit()

        return jsonify({
            "status": "Granted",
            "attendance": attendance_status,
            "student": {
                "name": f"{row['First_Name']} {row['Last_Name']}",
                "first_name": row['First_Name'],
                "last_name": row['Last_Name'],
                "student_number": row['Student_Number'],
                "email": row['Email'],
                "course": row['Course'],
                "faculty": row['Faculty'],
                "expiry_date": row['Expiry_Date'].isoformat(),
                "card_status": row['Card_Status'],
            },
            "module": {
                "code": module_row['Module_Code'] if module_row else None,
                "name": module_row['Module_Name'] if module_row else None,
                "venue": module_row['Venue'] if module_row else None,
                "day": module_row['Day'] if module_row else None,
                "time": module_row['Module_Time'] if module_row else None,
            } if module_row else None,
        }), 200

    except mysql.connector.Error:
        conn.rollback()
        logger.exception("DB error in verify_qr")
        return jsonify({"message": "Could not verify QR. Please try again."}), 500
    finally:
        cursor.close()
        conn.close()


# ============================================
# STATUS  (student only)
# ============================================

@qr_bp.route('/status', methods=['GET'])
def get_card_status():
    if session.get('role') != 'student':
        return jsonify({"message": "Student login required"}), 401

    student_id = session.get('student_id')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            '''
            SELECT Card_ID, Issue_Date, Expiry_Date, Card_Status
            FROM DIGITAL_ACCESS_CARD
            WHERE Student_ID = %s
            ORDER BY Expiry_Date DESC
            LIMIT 1
            ''',
            (student_id,)
        )
        card = cursor.fetchone()

        if not card:
            return jsonify({"message": "No digital card found"}), 404

        return jsonify({
            "card_id": card['Card_ID'],
            "status": card['Card_Status'],
            "issue_date": card['Issue_Date'].isoformat(),
            "expiry_date": card['Expiry_Date'].isoformat(),
            "days_until_expiry": (card['Expiry_Date'] - _now_sast().date()).days,
        }), 200

    except mysql.connector.Error:
        logger.exception("DB error in get_card_status")
        return jsonify({"message": "Could not fetch card status. Please try again."}), 500
    finally:
        cursor.close()
        conn.close()


# ============================================
# PHONE LANDING PAGE  (opened by scanning the QR with a camera)
# ============================================

@qr_page_bp.route('/qr/<int:student_id>/<token_uuid>')
def qr_landing(student_id, token_uuid):
    """Read-only card page. It never records attendance by itself:
    a logged-in staff member's page asks /api/qr/verify to do that."""
    is_staff = session.get('role') in ('Administrator', 'Security Personnel')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        row, error = _validate_card(conn, cursor, student_id, token_uuid.lower())
    except mysql.connector.Error:
        logger.exception("DB error in qr_landing")
        return render_template(
            'qr_landing.html', valid=False, is_staff=False,
            message="Could not check this QR code. Please try again."
        ), 500
    finally:
        cursor.close()
        conn.close()

    if error:
        return render_template(
            'qr_landing.html', valid=False, is_staff=False, message=error[0]
        ), error[1]

    return render_template(
        'qr_landing.html',
        valid=True,
        is_staff=is_staff,
        student={
            'name': f"{row['First_Name']} {row['Last_Name']}",
            'student_number': row['Student_Number'],
            'course': row['Course'],
            'faculty': row['Faculty'],
            'card_status': row['Card_Status'],
            'expiry_date': row['Expiry_Date'].isoformat(),
            'email': row['Email'] if is_staff else None,
        },
        qr_url=request.url,
    )
