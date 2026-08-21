<<<<<<< HEAD

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
=======
from flask import Blueprint, render_template, redirect, url_for, session, flash, abort
>>>>>>> 7b0d565c78d83e463c4f01e81de2306d1ad88a7a
import mysql.connector
import bcrypt
from functools import wraps
from config import Config
<<<<<<< HEAD
import bcrypt
from functools import wraps
=======
from forms.login import LoginForm

>>>>>>> 7b0d565c78d83e463c4f01e81de2306d1ad88a7a

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
<<<<<<< HEAD
# Role-based access control decorator
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('role')
            if user_role not in allowed_roles:
                abort(403)  # HTTP 403 Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()  # email for admin, student number for student
        password = request.form.get('password', '')

        if not identifier or not password:
            flash('Please enter both identifier and password', 'error')
=======

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

>>>>>>> 7b0d565c78d83e463c4f01e81de2306d1ad88a7a
            return redirect(url_for('auth.login'))

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

<<<<<<< HEAD
        # Check Admin login
        cursor.execute('SELECT * FROM ADMIN WHERE Email = %s', (identifier,))
        admin_user = cursor.fetchone()

        if admin_user and bcrypt.checkpw(password.encode('utf-8'), admin_user['Password_Hash'].encode('utf-8')):
            session['user_id'] = admin_user['Admin_ID']
            session['user_name'] = f"{admin_user['First_Name']} {admin_user['Last_Name']}"
            session['role'] = admin_user['Role']
            cursor.close()
            conn.close()
            return redirect(url_for('admin.dashboard'))  # update to your admin route

        # Check Student login
        cursor.execute('SELECT * FROM STUDENT WHERE Student_Number = %s', (identifier,))
=======

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

>>>>>>> 7b0d565c78d83e463c4f01e81de2306d1ad88a7a
        student_user = cursor.fetchone()

        cursor.close()
        conn.close()

<<<<<<< HEAD
        if student_user and bcrypt.checkpw(password.encode('utf-8'), student_user['Password_Hash'].encode('utf-8')):
            session['user_id'] = student_user['Student_ID']
            session['user_name'] = f"{student_user['First_Name']} {student_user['Last_Name']}"
            session['role'] = 'student'
            return redirect(url_for('student.dashboard'))  # update to your student route

        flash('Invalid identifier or password', 'error')
        return redirect(url_for('auth.login'))

    return render_template('login.html')
=======

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
    return render_template('staff-dashboard.html')
>>>>>>> 7b0d565c78d83e463c4f01e81de2306d1ad88a7a

# ============================================
# LOGOUT
# ============================================

@auth_bp.route('/logout')
def logout():

    session.clear()
<<<<<<< HEAD
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))
# Example protected route
@auth_bp.route('/dashboard')
@role_required('student')
def dashboard():
    return "Welcome to the Student Dashboard"
=======

    flash(
        'You have been logged out',
        'success'
    )

    return redirect(
        url_for('auth.login')
    )
>>>>>>> 7b0d565c78d83e463c4f01e81de2306d1ad88a7a
