import qrcode
import json
import uuid
from io import BytesIO
import base64

def generate_qr_data(student_id):
    """
    Generate unique QR code data for a student.
    """
    token_data = {
        "student_id": student_id,
        "token": str(uuid.uuid4()),
        "timestamp": str(datetime.now())
    }
    return json.dumps(token_data)

def create_qr_image(data):
    """
    Generate QR code image from data.
    """
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def generate_base64_qr(student_id):
    """
    Generate QR code and return as base64 string for frontend display.
    """
    qr_data = generate_qr_data(student_id)
    img = create_qr_image(qr_data)
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        "qr_data": qr_data,
        "qr_image": f"data:image/png;base64,{img_str}"
    }