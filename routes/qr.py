
"""
QR generation and verification routes for SmartAccess Campus.

Endpoints:
GET  /api/qr/generate - Student generates their own QR code.
POST /api/qr/verify   - Staff verifies a scanned QR code.
GET  /api/qr/status   - Student checks their card status.
"""

import logging
from datetime import datetime, timedelta, timezone

import mysql.connector
from flask import Blueprint, jsonify, request, session

from config import Config
from routes.auth import role_required
from utils.qr_utils import generate_base64_qr, decode_qr_token


# ============================================
# CONFIGURATION
# ============================================

logger = logging.getLogger(__name__)

qr_bp = Blueprint('qr', __name__, url_prefix='/api/qr')

api_staff_required = role_required(
    'Administrator',
    'Security Personnel'
)

# QR tokens expire after 24 hours.
TOKEN_TTL_HOURS = 24

# South African Standard Time (UTC+2).
SAST = timezone(timedelta(hours=2))


# ============================================
# DATABASE CONNECTION
# ============================================

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
# GENERATE QR
# Student only
# ============================================

@qr_bp.route('/generate', methods=['GET'])
def generate_qr():

    if session.get('role') != 'student':
        return jsonify({
            "message": "Student login required"
        }), 401

    student_id = session.get('student_id')

    if not student_id:
        return jsonify({
            "message": "Session missing student_id"
        }), 401

    conn = None
    cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # Find the student.
        cursor.execute(
            '''
            SELECT Student_Number
            FROM STUDENT
            WHERE Student_ID = %s
            ''',
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "message": "Student not found"
            }), 404

        # Find the latest access card.
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

            # Do not reactivate suspended or revoked cards.
            if card['Card_Status'] in ('Suspended', 'Revoked'):
                return jsonify({
                    "message": (
                        f"Your access card is "
                        f"{card['Card_Status'].lower()}. "
                        "Please contact administration."
                    )
                }), 403

            # Update the existing card.
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

            # Create a new digital access card.
            cursor.execute(
                '''
                INSERT INTO DIGITAL_ACCESS_CARD
                    (
                        Student_ID,
                        QR_Code_Data,
                        Issue_Date,
                        Expiry_Date,
                        Card_Status
                    )
                VALUES (%s, %s, %s, %s, 'Active')
                ''',
                (student_id, '', today, new_expiry)
            )

            card_id = cursor.lastrowid

        # Generate the QR code.
        qr_result = generate_base64_qr(
            student_id,
            student['Student_Number']
        )

        # Save the generated QR token.
        cursor.execute(
            '''
            UPDATE DIGITAL_ACCESS_CARD
            SET QR_Token = %s,
                Token_Issued_At = %s,
                QR_Code_Data = %s
            WHERE Card_ID = %s
            ''',
            (
                qr_result['uuid'],
                _now_sast(),
                qr_result['token'],
                card_id
            )
        )

        conn.commit()

        return jsonify({
            "message": "QR code generated",
            "qr": {
                "image": qr_result['image'],
                "token": qr_result['token']
            }
        }), 200

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        logger.exception("QR DATABASE ERROR: %s", e)

        return jsonify({
            "message": "Could not generate QR. Please try again."
        }), 500

    except Exception as e:

        if conn:
            conn.rollback()

        logger.exception("QR GENERATION ERROR: %s", e)

        return jsonify({
            "message": "Could not generate QR. Please try again."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()



# ============================================
# VERIFY QR
# Staff only
# ============================================

@qr_bp.route('/verify', methods=['POST'])
@api_staff_required
def verify_qr():

    data = request.get_json(silent=True) or {}
    qr_data = data.get('qr_data')

    if not qr_data:
        return jsonify({
            "message": "QR data is required."
        }), 400

    # Decode the scanned QR code.
    payload = decode_qr_token(qr_data)

    if not payload:
        return jsonify({
            "message": "Invalid QR code."
        }), 400

    try:
        student_id = int(payload.get('student_id'))
        student_number = payload.get('student_number')
        token = payload.get('token')
    except (TypeError, ValueError):
        return jsonify({
            "message": "Invalid QR information."
        }), 400

    if not student_number or not token:
        return jsonify({
            "message": "QR information is incomplete."
        }), 400

    conn = None
    cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        now = _now_sast()

        # Find the student's access card and details.
        cursor.execute("""
            SELECT
                s.Student_ID,
                s.First_Name,
                s.Last_Name,
                s.Student_Number,
                s.Email,
                s.Course,
                s.Faculty,
                c.Card_ID,
                c.Expiry_Date,
                c.Card_Status,
                c.QR_Token,
                c.Token_Issued_At
            FROM DIGITAL_ACCESS_CARD c
            JOIN STUDENT s
                ON s.Student_ID = c.Student_ID
            WHERE c.Student_ID = %s
            LIMIT 1
        """, (student_id,))

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "message": "Student or access card not found."
            }), 404

        # Check student number.
        if student['Student_Number'] != student_number:
            return jsonify({
                "message": "Student information does not match."
            }), 403

        # Check QR token.
        if not student['QR_Token'] or student['QR_Token'] != token:
            return jsonify({
                "message": "Invalid or replaced QR token."
            }), 403

        # Check card status.
        if student['Card_Status'] != 'Active':
            return jsonify({
                "message": "Student access card is not active."
            }), 403

        # Check card expiry.
        if student['Expiry_Date'] < now.date():
            return jsonify({
                "message": "Student access card has expired."
            }), 403

        # Check token issue time.
        issued_at = student['Token_Issued_At']

        if not issued_at:
            return jsonify({
                "message": "QR token issue time is missing."
            }), 403

        token_age = now - issued_at

        if token_age > timedelta(hours=TOKEN_TTL_HOURS):
            return jsonify({
                "message": "QR code has expired. Generate a new one."
            }), 403

        # Find the student's enrolled module.
        cursor.execute("""
            SELECT
                m.Module_ID,
                m.Module_Name,
                m.Module_Code,
                m.Venue
            FROM STUDENT_MODULE sm
            JOIN MODULE m
                ON m.Module_ID = sm.Module_ID
            WHERE sm.Student_ID = %s
            ORDER BY m.Module_ID
            LIMIT 1
        """, (student_id,))

        module = cursor.fetchone()

        attendance_message = "Attendance not recorded."
        
        if module:

            # Check whether attendance was already recorded today.
            cursor.execute("""
                SELECT Attendance_ID
                FROM ATTENDANCE
                WHERE Student_ID = %s
                  AND Module_ID = %s
                  AND Attendance_Date = %s
                LIMIT 1
            """, (
                student_id,
                module['Module_ID'],
                now.date()
            ))

            existing_attendance = cursor.fetchone()

            if existing_attendance:
                attendance_message = "Attendance already recorded today."

            else:
                # Record attendance.
                cursor.execute("""
                    INSERT INTO ATTENDANCE (
                        Student_ID,
                        Module_ID,
                        Attendance_Date,
                        Status,
                        Scan_Time,
                        Gate_Location
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    student_id,
                    module['Module_ID'],
                    now.date(),
                    'Present',
                    now.time().replace(microsecond=0),
                    'Main Gate'
                ))

                attendance_message = "Attendance recorded successfully."

        else:
            attendance_message = "No enrolled module found. Attendance not recorded."

        conn.commit()

        return jsonify({
            "status": "Granted",
            "message": "Student verified successfully.",
            "attendance": attendance_message,
            "student": {
                "name": (
                    f"{student['First_Name']} "
                    f"{student['Last_Name']}"
                ),
                "first_name": student['First_Name'],
                "last_name": student['Last_Name'],
                "student_number": student['Student_Number'],
                "email": student['Email'],
                "course": student['Course'],
                "faculty": student['Faculty'],
                "expiry_date": str(student['Expiry_Date']),
                "card_status": student['Card_Status']
            },
            "module": {
                "module_id": module['Module_ID'],
                "module_name": module['Module_Name'],
                "module_code": module['Module_Code'],
                "venue": module['Venue']
            } if module else None
        }), 200

    except mysql.connector.Error:
        if conn:
            conn.rollback()

        logger.exception("QR VERIFICATION DATABASE ERROR")

        return jsonify({
            "message": "Could not verify QR code. Please try again."
        }), 500

    except Exception:
        if conn:
            conn.rollback()

        logger.exception("QR VERIFICATION ERROR")

        return jsonify({
            "message": "QR verification failed."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

# ============================================
# GET CARD STATUS
# Student only
# ============================================

@qr_bp.route('/status', methods=['GET'])
def get_card_status():

    if session.get('role') != 'student':
        return jsonify({
            "message": "Student login required"
        }), 401

    student_id = session.get('student_id')

    if not student_id:
        return jsonify({
            "message": "Session missing student_id"
        }), 401

    conn = None
    cursor = None

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            '''
            SELECT
                Card_ID,
                Issue_Date,
                Expiry_Date,
                Card_Status
            FROM DIGITAL_ACCESS_CARD
            WHERE Student_ID = %s
            ORDER BY Expiry_Date DESC
            LIMIT 1
            ''',
            (student_id,)
        )

        card = cursor.fetchone()

        if not card:
            return jsonify({
                "message": "No digital card found"
            }), 404

        days_until_expiry = (
            card['Expiry_Date'] - _now_sast().date()
        ).days

        return jsonify({
            "card_id": card['Card_ID'],
            "status": card['Card_Status'],
            "issue_date": card['Issue_Date'].isoformat(),
            "expiry_date": card['Expiry_Date'].isoformat(),
            "days_until_expiry": days_until_expiry
        }), 200

    except mysql.connector.Error as e:

        logger.exception("CARD STATUS DATABASE ERROR: %s", e)

        return jsonify({
            "message": "Could not fetch card status. Please try again."
        }), 500

    except Exception as e:

        logger.exception("CARD STATUS ERROR: %s", e)

        return jsonify({
            "message": "Could not fetch card status. Please try again."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
