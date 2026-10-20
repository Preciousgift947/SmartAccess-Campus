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

# How long a generated token stays valid. Set to 0 for no expiry.
TOKEN_TTL_HOURS = 24


# ============================================
# DATABASE CONNECTION (same pattern as auth.py)
# ============================================

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
        return jsonify({"msg": "Student login required"}), 401

    student_id = session.get('student_id')
    if not student_id:
        return jsonify({"msg": "Session missing student_id"}), 401

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        'SELECT Student_Number FROM STUDENT WHERE Student_ID = %s',
        (student_id,)
    )
    student = cursor.fetchone()

    if not student:
        cursor.close()
        conn.close()
        return jsonify({"msg": "Student not found"}), 404

    cursor.execute(
        '''
        SELECT Card_ID, Expiry_Date, Card_Status
        FROM digital_access_card
        WHERE Student_ID = %s AND Card_Status = 'Active'
        ORDER BY Expiry_Date DESC
        LIMIT 1
        ''',
        (student_id,)
    )
    card = cursor.fetchone()

    today = datetime.utcnow().date()

    if not card or card['Expiry_Date'] < today:
        expiry = today + timedelta(days=365)
        cursor.execute(
            '''
            INSERT INTO digital_access_card
                (Student_ID, QR_Code_Data, Issue_Date, Expiry_Date, Card_Status)
            VALUES (%s, %s, %s, %s, 'Active')
            ''',
            (student_id, '', today, expiry)
        )
        conn.commit()

    # Generate QR (returns token, uuid, image)
    qr_result = generate_base64_qr(student_id, student['Student_Number'])

    # Persist the UUID + issue timestamp so /verify can validate later
    cursor.execute(
        '''
        UPDATE digital_access_card
        SET QR_Token = %s,
            Token_Issued_At = %s,
            QR_Code_Data = %s
        WHERE Student_ID = %s AND Card_Status = 'Active'
        ''',
        (qr_result['uuid'], datetime.utcnow(), qr_result['token'], student_id)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "msg": "QR code generated",
        "qr": {
            "image": qr_result['image'],
            "token": qr_result['token'],
        }
    }), 200


# ============================================
# VERIFY QR  (public — security scanner calls it)
# ============================================

@qr_bp.route('/verify', methods=['POST'])
def verify_qr():
    data = request.get_json(silent=True) or {}
    qr_token = data.get('qr_data')

    if not qr_token:
        return jsonify({"msg": "No QR data provided"}), 400

    parsed = decode_qr_token(qr_token)
    if not parsed or 'student_id' not in parsed or 'token' not in parsed:
        return jsonify({"msg": "Invalid QR code format"}), 400

    student_id = parsed['student_id']
    token_uuid = parsed['token']

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Pull the student and their most recent active card in one query
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
        FROM digital_access_card c
        JOIN STUDENT s ON s.Student_ID = c.Student_ID
        WHERE c.Student_ID = %s AND c.Card_Status = 'Active'
        ORDER BY c.Expiry_Date DESC
        LIMIT 1
        ''',
        (student_id,)
    )
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return jsonify({"msg": "No active card found"}), 403

    # ── TOKEN VALIDATION ──
    if not row['QR_Token'] or row['QR_Token'] != token_uuid:
        cursor.close()
        conn.close()
        return jsonify({"msg": "Invalid or revoked QR token"}), 401

    # ── CARD EXPIRY ──
    if row['Expiry_Date'] < datetime.utcnow().date():
        cursor.execute(
            "UPDATE digital_access_card SET Card_Status = 'Expired' WHERE Card_ID = %s",
            (row['Card_ID'],)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"msg": "Card expired"}), 403

    # ── TOKEN TTL (optional) ──
    if TOKEN_TTL_HOURS > 0 and row['Token_Issued_At']:
        age = datetime.utcnow() - row['Token_Issued_At']
        if age > timedelta(hours=TOKEN_TTL_HOURS):
            cursor.close()
            conn.close()
            return jsonify({"msg": "QR token expired, please regenerate"}), 401

    cursor.close()
    conn.close()

    return jsonify({
        "status": "Granted",
        "student": {
            "name": f"{row['First_Name']} {row['Last_Name']}",
            "student_number": row['Student_Number'],
            "course": row['Course'],
        }
    }), 200


# ============================================
# STATUS  (student only)
# ============================================

@qr_bp.route('/status', methods=['GET'])
def get_card_status():
    if session.get('role') != 'student':
        return jsonify({"msg": "Student login required"}), 401

    student_id = session.get('student_id')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        '''
        SELECT Card_ID, Issue_Date, Expiry_Date, Card_Status
        FROM digital_access_card
        WHERE Student_ID = %s
        ORDER BY Expiry_Date DESC
        LIMIT 1
        ''',
        (student_id,)
    )
    card = cursor.fetchone()
    cursor.close()
    conn.close()

    if not card:
        return jsonify({"msg": "No digital card found"}), 404

    return jsonify({
        "card_id": card['Card_ID'],
        "status": card['Card_Status'],
        "issue_date": card['Issue_Date'].isoformat(),
        "expiry_date": card['Expiry_Date'].isoformat(),
        "days_until_expiry": (card['Expiry_Date'] - datetime.utcnow().date()).days,
    }), 200