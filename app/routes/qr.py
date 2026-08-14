from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.qr_utils import generate_base64_qr, generate_qr_data
from ..models.student import Student
from ..models.digital_card import DigitalAccessCard
from ..extensions import db
from datetime import datetime, timedelta

bp = Blueprint('qr', __name__, url_prefix='/api/qr')

@bp.route('/generate', methods=['GET'])
@jwt_required()
def generate_student_qr():
    """
    Generate QR code for the authenticated student.
    """
    student_id = get_jwt_identity()
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({"msg": "Student not found"}), 404
    
    # Check if student has a digital card
    card = DigitalAccessCard.query.filter_by(student_id=student_id).first()
    
    if not card:
        # Create new card
        qr_result = generate_base64_qr(student_id)
        card = DigitalAccessCard(
            student_id=student_id,
            qr_code_data=qr_result['qr_data'],
            issue_date=datetime.now().date(),
            expiry_date=datetime.now().date() + timedelta(days=365),
            card_status='Active'
        )
        db.session.add(card)
        db.session.commit()
        return jsonify(qr_result), 201
    else:
        # Return existing QR
        qr_result = generate_base64_qr(student_id)
        return jsonify(qr_result), 200

@bp.route('/verify', methods=['POST'])
def verify_qr():
    """
    Verify QR code for campus entry (Security Personnel use this).
    """
    data = request.get_json()
    qr_token = data.get('qr_data')
    
    if not qr_token:
        return jsonify({"msg": "No QR data provided"}), 400
    
    try:
        # Parse QR data
        qr_info = json.loads(qr_token)
        student_id = qr_info.get('student_id')
        
        # Check if student exists
        student = Student.query.get(student_id)
        if not student:
            return jsonify({"msg": "Invalid QR code"}), 404
        
        # Check if card is active
        card = DigitalAccessCard.query.filter_by(student_id=student_id).first()
        if not card or card.card_status != 'Active':
            return jsonify({"msg": "Card is not active"}), 403
        
        if card.expiry_date < datetime.now().date():
            return jsonify({"msg": "Card has expired"}), 403
        
        # Record attendance (will be implemented later)
        # ...
        
        return jsonify({
            "status": "Granted",
            "student": {
                "name": f"{student.first_name} {student.last_name}",
                "student_number": student.student_number,
                "course": student.course
            }
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({"msg": "Invalid QR code format"}), 400