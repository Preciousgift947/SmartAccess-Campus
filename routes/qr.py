"""
QR generation and verification routes for SmartAccess Campus.

Endpoints:
  GET  /api/qr/generate  - student fetches their own QR (session required)
  POST /api/qr/verify    - security staff verifies a scanned QR (public)
  GET  /api/qr/status    - student fetches their card status

Token security: the UUID in the QR payload is stored on the card row at
generation time. /verify rejects any token that doesn't match the stored
value — this prevents forged or replayed tokens from granting access.
"""
from flask import Blueprint, jsonify, request, session
import mysql.connector
from datetime import datetime, timedelta

from config import Config
from utils.qr_utils import generate_base64_qr, decode_qr_token


qr_bp = Blueprint('qr', __name__, url_prefix='/api/qr')

TOKEN_TTL_HOURS = 24


def get_db():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT
    )


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

        today = datetime.utcnow().date()
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

        qr_result = generate_base64_qr(student_id, student['Student_Number'])

        cursor.execute(
            '''
            UPDATE DIGITAL_ACCESS_CARD
            SET QR_Token = %s,
                Token_Issued_At = %s,
                QR_Code_Data = %s
            WHERE Card_ID = %s
            ''',
            (qr_result['uuid'], datetime.utcnow(), qr_result['token'], card_id)
        )
        conn.commit()

        return jsonify({
            "message": "QR code generated",
            "qr": {
                "image": qr_result['image'],
                "token": qr_result['token'],
            }
        }), 200

    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"message": f"Database error: {e}"}), 500
    finally:
        cursor.close()
        conn.close()


# ============================================
# VERIFY QR  (public — security scanner calls it)
# ============================================

@qr_bp.route('/verify', methods=['POST'])
def verify_qr():
    data = request.get_json(silent=True) or {}
    qr_token = data.get('qr_data')

    if not qr_token:
        return jsonify({"message": "No QR data provided"}), 400

    parsed = decode_qr_token(qr_token)
    if not parsed or 'student_id' not in parsed or 'token' not in parsed:
        return jsonify({"message": "Invalid QR code format"}), 400

    student_id = parsed['student_id']
    token_uuid = parsed['token']

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
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
                   s.Course
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
            return jsonify({"message": "No active card found"}), 403

        # ── TOKEN VALIDATION ──
        if not row['QR_Token'] or row['QR_Token'] != token_uuid:
            return jsonify({"message": "Invalid or revoked QR token"}), 401

        # ── CARD EXPIRY ──
        if row['Expiry_Date'] < datetime.utcnow().date():
            cursor.execute(
                "UPDATE DIGITAL_ACCESS_CARD SET Card_Status = 'Expired' WHERE Card_ID = %s",
                (row['Card_ID'],)
            )
            conn.commit()
            return jsonify({"message": "Card expired"}), 403

        # ── TOKEN TTL ──
        if TOKEN_TTL_HOURS > 0 and row['Token_Issued_At']:
            age = datetime.utcnow() - row['Token_Issued_At']
            if age > timedelta(hours=TOKEN_TTL_HOURS):
                return jsonify({"message": "QR token expired, please regenerate"}), 401

        # ── Record attendance (module is first enrolled) ──
        cursor.execute(
            '''
            SELECT Module_ID FROM STUDENT_MODULE
            WHERE Student_ID = %s
            ORDER BY Module_ID
            LIMIT 1
            ''',
            (student_id,)
        )
        module_row = cursor.fetchone()
        module_id = module_row['Module_ID'] if module_row else None

        if module_id:
            now = datetime.utcnow()
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
                    data.get('gate_location', 'Main Entrance')
                )
            )
            conn.commit()

        return jsonify({
            "status": "Granted",
            "student": {
                "name": f"{row['First_Name']} {row['Last_Name']}",
                "student_number": row['Student_Number'],
                "course": row['Course'],
            }
        }), 200

    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"message": f"Database error: {e}"}), 500
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
            "days_until_expiry": (card['Expiry_Date'] - datetime.utcnow().date()).days,
        }), 200

    except mysql.connector.Error as e:
        return jsonify({"message": f"Database error: {e}"}), 500
    finally:
        cursor.close()
        conn.close()