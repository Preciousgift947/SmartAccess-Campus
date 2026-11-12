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
import re
from datetime import datetime

# A scanned phone link looks like  https://host/qr/<student_id>/<token-uuid>
_QR_URL_RE = re.compile(
    r"/qr/(\d+)/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})/?(?:[?#].*)?$"
)


def generate_base64_qr(student_id, student_number, base_url=None):
    """
    Returns dict with:
      - token: what is embedded in the QR (a link when base_url is given,
               otherwise the old JSON text)
      - uuid:  the raw UUID (store this in the DB for verification)
      - image: data:image/png;base64,... URI for <img src>

    With a base_url the QR holds a link, so a phone camera opens the card page.
    """
    uuid_str = str(uuid.uuid4())

    if base_url:
        token = f"{base_url.rstrip('/')}/qr/{int(student_id)}/{uuid_str}"
    else:
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
    """Parse a scanned QR string (link or old JSON) into a dict, or None."""
    if isinstance(qr_string, str):
        match = _QR_URL_RE.search(qr_string.strip())
        if match:
            return {"student_id": int(match.group(1)), "token": match.group(2).lower()}
    try:
        data = json.loads(qr_string)
    except (json.JSONDecodeError, TypeError):
        return None
    return data if isinstance(data, dict) else None