from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
import mysql.connector
from config import Config
import bcrypt

auth_bp = Blueprint('auth', __name__)

def get_db():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT
    )

# ============================================
# LOGIN PAGE
# ============================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_number = request.form.get('student_number', '').strip()
        password = request.form.get('password', '')

        # Basic input validation
        if not student_number or not password:
            flash('Please enter both student number and password', 'error')
            return redirect(url_for('auth.login'))

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            'SELECT * FROM STUDENT WHERE Student_Number = %s',
            (student_number,)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['Password_Hash'].encode('utf-8')):
            session['student_id'] = user['Student_ID']
            session['student_name'] = f"{user['First_Name']} {user['Last_Name']}"
            session['student_number'] = user['Student_Number']
            session['course'] = user['Course']
            session['faculty'] = user['Faculty']
            session['role'] = user.get('Role', 'student')  # Default role 'student'

            return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid student number or password', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# ============================================
# LOGOUT
# ============================================
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))
