
from flask import Flask, session, redirect, url_for, flash
from datetime import timedelta, datetime, timezone

from config import Config
from routes.auth import auth_bp
from routes.student import student_bp
from routes.qr import qr_bp

app = Flask(__name__)
app.config.from_object(Config)

# Check that the secret key is configured
if not app.config.get('SECRET_KEY'):
    raise RuntimeError("SECRET_KEY is missing from environment configuration.")

# Session configuration
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(qr_bp)


# Session timeout handler
@app.before_request
def make_session_permanent():
    if 'user_id' not in session and 'student_id' not in session:
        return

    session.permanent = True

    now = datetime.now(timezone.utc).timestamp()
    last_activity = session.get('last_activity')

    if last_activity:
        elapsed = now - float(last_activity)

        if elapsed > 1800:
            session.clear()
            flash('Session timed out. Please log in again.', 'info')
            return redirect(url_for('auth.login'))

    session['last_activity'] = now


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=5000)

