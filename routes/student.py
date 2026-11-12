from flask import Blueprint, render_template, redirect, url_for, session, jsonify
import mysql.connector
from config import Config

student_bp = Blueprint('student', __name__)


def get_db():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT
    )


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated_function


def api_login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            return jsonify({"success": False, "message": "Not logged in"}), 401

        return f(*args, **kwargs)

    return decorated_function


# ============================================
# HOME - students only ever see their QR code
# ============================================

@student_bp.route('/')
@login_required
def home():
    return redirect(url_for('student.digital_id'))


# ============================================
# QR CODE PAGE (the only student page)
# ============================================

@student_bp.route('/digital_id')
@login_required
def digital_id():
    return render_template('digital_id.html')
