from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..models.student import Student
from ..extensions import db
import bcrypt

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Email and password required"}), 400
    
    # Check if student already exists
    if Student.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Student already exists"}), 409
    
    # Hash password
    hashed_password = bcrypt.hashpw(
        data['password'].encode('utf-8'), 
        bcrypt.gensalt()
    )
    
    # Create student
    student = Student(
        first_name=data['first_name'],
        last_name=data['last_name'],
        student_number=data['student_number'],
        email=data['email'],
        phone_number=data.get('phone_number'),
        course=data['course'],
        faculty=data['faculty'],
        registration_date=date.today(),
        password_hash=hashed_password.decode('utf-8')
    )
    
    db.session.add(student)
    db.session.commit()
    
    return jsonify({"msg": "Student registered successfully"}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    student = Student.query.filter_by(email=data.get('email')).first()
    
    if not student or not bcrypt.checkpw(
        data.get('password', '').encode('utf-8'), 
        student.password_hash.encode('utf-8')
    ):
        return jsonify({"msg": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=student.student_id)
    return jsonify({
        "access_token": access_token,
        "student_id": student.student_id,
        "name": f"{student.first_name} {student.last_name}"
    }), 200