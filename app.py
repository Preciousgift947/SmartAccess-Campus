from flask import Flask, session, redirect, url_for, flash
from datetime import timedelta, datetime, timezone
from config import Config
from routes.auth import auth_bp
from routes.student import student_bp

app = Flask(__name__)
app.config.from_object(Config)

# Session configuration  # Replace with a strong secret key
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)

# Session timeout handler
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

    now = datetime.now(timezone.utc)
    last_activity = session.get('last_activity')

    if last_activity:
        # Convert old timezone-naive datetime if necessary
        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)

        elapsed = (now - last_activity).total_seconds()

        if elapsed > 1800:
            session.clear()
            flash('Session timed out. Please log in again.', 'info')
            return redirect(url_for('auth.login'))

    session['last_activity'] = now

# ============================================
# RUN THE APP
# ============================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
