"""
QR utility functions for SmartAccess Campus.

- generate_base64_qr: builds a signed-looking token, encodes it as a QR
  PNG, and returns the data URI + the raw UUID (for storage).
- decode_qr_token: parses the JSON payload from a scanned QR string.
"""
import qrcode
import json
import uuid
from io import BytesIO
import base64
from datetime import datetime


def generate_base64_qr(student_id, student_number):
    """
    Returns dict with:
      - token: JSON string embedded in the QR
      - uuid:  the raw UUID (store this in the DB for verification)
      - image: data:image/png;base64,... URI for <img src>
    """
    uuid_str = str(uuid.uuid4())
    payload = {
        "student_id": student_id,
        "student_number": student_number,
        "token": uuid_str,
        "issued_at": datetime.utcnow().isoformat(),
    }
    token = json.dumps(payload)

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()

    return {
        "token": token,
        "uuid": uuid_str,
        "image": f"data:image/png;base64,{img_b64}",
    }


def decode_qr_token(qr_string):
    """Parse a scanned QR string back into a dict, or None on failure."""
    try:
        return json.loads(qr_string)
    except (json.JSONDecodeError, TypeError):
        return None