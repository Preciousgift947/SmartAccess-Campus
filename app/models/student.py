from ..extensions import db

class Student(db.Model):
    __tablename__ = 'students'
    
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    student_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15))
    photo_url = db.Column(db.String(255))
    course = db.Column(db.String(100), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    registration_date = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Relationships
    digital_card = db.relationship('DigitalAccessCard', backref='student', uselist=False)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    notifications = db.relationship('Notification', backref='student', lazy=True)