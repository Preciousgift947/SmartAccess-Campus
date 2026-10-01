from flask import Blueprint, render_template, redirect, url_for, session, flash, abort, jsonify, request
import mysql.connector
import bcrypt
from functools import wraps

from config import Config
from forms.login import LoginForm


auth_bp = Blueprint('auth', __name__)


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


# ============================================
# ROLE-BASED ACCESS CONTROL
# ============================================

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('role')

            if user_role not in allowed_roles:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# ============================================
# LOGIN
# ============================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        identifier = form.identifier.data.strip()
        password = form.password.data

        if not identifier or not password:
            flash(
                'Please enter both identifier and password',
                'error'
            )
            return redirect(url_for('auth.login'))

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # ====================================
        # CHECK ADMIN LOGIN
        # ====================================

        cursor.execute(
            'SELECT * FROM ADMIN WHERE Email = %s',
            (identifier,)
        )

        admin_user = cursor.fetchone()

        if admin_user and bcrypt.checkpw(
            password.encode('utf-8'),
            admin_user['Password_Hash'].encode('utf-8')
        ):
            session.clear()

            session['user_id'] = admin_user['Admin_ID']

            session['user_name'] = (
                f"{admin_user['First_Name']} "
                f"{admin_user['Last_Name']}"
            )

            session['role'] = admin_user['Role']

            cursor.close()
            conn.close()

            return redirect(
                url_for('auth.staff_dashboard')
            )

        # ====================================
        # CHECK STUDENT LOGIN
        # ====================================

        cursor.execute(
            '''
            SELECT *
            FROM STUDENT
            WHERE Student_Number = %s
            ''',
            (identifier,)
        )

        student_user = cursor.fetchone()

        cursor.close()
        conn.close()

        if student_user and bcrypt.checkpw(
            password.encode('utf-8'),
            student_user['Password_Hash'].encode('utf-8')
        ):
            session.clear()

            session['student_id'] = student_user['Student_ID']

            session['student_name'] = (
                f"{student_user['First_Name']} "
                f"{student_user['Last_Name']}"
            )

            session['user_name'] = session['student_name']
            session['course'] = student_user['Course']
            session['role'] = 'student'

            return redirect(
                url_for('student.dashboard')
            )

        # ====================================
        # INVALID LOGIN
        # ====================================

        flash(
            'Invalid identifier or password',
            'error'
        )

        return redirect(
            url_for('auth.login')
        )

    return render_template(
        'login.html',
        form=form
    )


# ============================================
# STAFF DASHBOARD
# ============================================

@auth_bp.route('/staff-dashboard')
@role_required('Administrator', 'Security Personnel')
def staff_dashboard():
    return render_template('staff_dashboard.html')


# ============================================
# LOGOUT
# ============================================

@auth_bp.route('/logout')
def logout():
    session.clear()

    flash(
        'You have been logged out',
        'success'
    )

    return redirect(
        url_for('auth.login')
    )


# ============================================
# API ENDPOINTS
# ============================================

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({
            'success': False,
            'message': 'Please provide identifier and password'
        }), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Check Admin Login
    cursor.execute(
        'SELECT * FROM ADMIN WHERE Email = %s',
        (identifier,)
    )

    admin_user = cursor.fetchone()

    if admin_user and bcrypt.checkpw(
        password.encode('utf-8'),
        admin_user['Password_Hash'].encode('utf-8')
    ):
        session.clear()
        session['user_id'] = admin_user['Admin_ID']
        session['user_name'] = (
            f"{admin_user['First_Name']} "
            f"{admin_user['Last_Name']}"
        )
        session['role'] = admin_user['Role']

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'role': 'admin',
            'user_name': session['user_name']
        }), 200

    # Check Student Login
    cursor.execute(
        'SELECT * FROM STUDENT WHERE Student_Number = %s',
        (identifier,)
    )

    student_user = cursor.fetchone()

    cursor.close()
    conn.close()

    if student_user and bcrypt.checkpw(
        password.encode('utf-8'),
        student_user['Password_Hash'].encode('utf-8')
    ):
        session.clear()
        session['student_id'] = student_user['Student_ID']
        session['student_name'] = (
            f"{student_user['First_Name']} "
            f"{student_user['Last_Name']}"
        )
        session['user_name'] = session['student_name']
        session['course'] = student_user['Course']
        session['role'] = 'student'

        return jsonify({
            'success': True,
            'role': 'student',
            'user_name': session['user_name'],
            'course': session['course']
        }), 200

    return jsonify({
        'success': False,
        'message': 'Invalid identifier or password'
    }), 401


@auth_bp.route('/api/profile')
def api_profile():
    if 'user_id' not in session and 'student_id' not in session:
        return jsonify({
            'success': False,
            'message': 'Not authenticated'
        }), 401

    return jsonify({
        'user_name': session.get('user_name'),
        'role': session.get('role'),
        'student_id': session.get('student_id'),
        'user_id': session.get('user_id'),
        'course': session.get('course')
    }), 200


@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()

    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200