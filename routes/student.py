from flask import Blueprint, render_template, redirect, url_for, session
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

# ============================================
# HOME - Redirect to Dashboard
# ============================================
@student_bp.route('/')
@login_required
def home():
    return redirect(url_for('student.dashboard'))

# ============================================
# DASHBOARD
# ============================================
@student_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Get card status
    cursor.execute(
        'SELECT * FROM DIGITAL_ACCESS_CARD WHERE Student_ID = %s',
        (session['student_id'],)
    )
    card = cursor.fetchone()
    
    # Get enrolled modules
    cursor.execute('''
        SELECT m.Module_Name, m.Module_Code, m.Venue, m.Day, m.Time
        FROM MODULE m
        JOIN STUDENT_MODULE sm ON m.Module_ID = sm.Module_ID
        WHERE sm.Student_ID = %s
    ''', (session['student_id'],))
    modules = cursor.fetchall()
    
    # Get notifications count
    cursor.execute(
        'SELECT COUNT(*) as count FROM NOTIFICATION WHERE Student_ID = %s AND Is_Read = FALSE',
        (session['student_id'],)
    )
    unread = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html',
                         card=card,
                         modules=modules,
                         unread_notifications=unread,
                         student_name=session['student_name'],
                         course=session['course'])

# ============================================
# STUDENT CARD
# ============================================
@student_bp.route('/card')
@login_required
def card():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT s.*, dac.Card_Status, dac.Expiry_Date, dac.Issue_Date
        FROM STUDENT s
        JOIN DIGITAL_ACCESS_CARD dac ON s.Student_ID = dac.Student_ID
        WHERE s.Student_ID = %s
    ''', (session['student_id'],))
    student = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('card.html', student=student)

# ============================================
# TIMETABLE
# ============================================
@student_bp.route('/timetable')
@login_required
def timetable():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT m.Module_Name, m.Module_Code, m.Venue, m.Day, m.Time,
               CONCAT(l.First_Name, ' ', l.Last_Name) as Lecturer_Name
        FROM MODULE m
        JOIN STUDENT_MODULE sm ON m.Module_ID = sm.Module_ID
        JOIN LECTURER l ON m.Lecturer_ID = l.Lecturer_ID
        WHERE sm.Student_ID = %s
        ORDER BY FIELD(m.Day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'), m.Time
    ''', (session['student_id'],))
    modules = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('timetable.html', modules=modules)

# ============================================
# NOTIFICATIONS
# ============================================
@student_bp.route('/notifications')
@login_required
def notifications():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT n.Notification_ID, n.Message, n.Sent_Date, n.Is_Read,
               ae.Event_Type, ae.Event_Date
        FROM NOTIFICATION n
        LEFT JOIN ACADEMIC_EVENT ae ON n.Event_ID = ae.Event_ID
        WHERE n.Student_ID = %s
        ORDER BY n.Sent_Date DESC
    ''', (session['student_id'],))
    notifications = cursor.fetchall()
    
    # Mark all as read
    cursor.execute(
        'UPDATE NOTIFICATION SET Is_Read = TRUE WHERE Student_ID = %s',
        (session['student_id'],)
    )
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return render_template('notifications.html', notifications=notifications)
