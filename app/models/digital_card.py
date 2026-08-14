from ..extensions import db

class DigitalAccessCard(db.Model):
    __tablename__ = 'digital_access_cards'
    
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), unique=True, nullable=False)
    qr_code_data = db.Column(db.Text, nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    card_status = db.Column(db.Enum('Active', 'Expired', 'Suspended', 'Revoked'), default='Active')