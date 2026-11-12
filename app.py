import os

from flask import Flask, session, redirect, url_for, flash
from datetime import timedelta, datetime, timezone
from config import Config
from routes.auth import auth_bp
from routes.student import student_bp
from routes.staff import staff_bp
from routes.qr import qr_bp, qr_page_bp

app = Flask(__name__)
app.config.from_object(Config)

# Session configuration  # Replace with a strong secret key
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Session cookies are only sent over HTTPS when this is on. Leave it off for
# local http use; set SESSION_COOKIE_SECURE=true in .env once the site is
# served over HTTPS.
app.config['SESSION_COOKIE_SECURE'] = (
    os.getenv('SESSION_COOKIE_SECURE', 'false').strip().lower()
    in ('1', 'true', 'yes')
)

# The secret key signs the session cookie, so it must be set and strong.
_secret = app.config.get('SECRET_KEY') or ''

if not _secret:
    raise RuntimeError(
        "SECRET_KEY is not set. Add a long random SECRET_KEY to your .env file "
        "(make one with: python -c \"import secrets; print(secrets.token_hex(32))\")."
    )

if len(_secret) < 32:
    if app.config['SESSION_COOKIE_SECURE']:
        raise RuntimeError(
            "SECRET_KEY is too short (needs at least 32 characters) when "
            "SESSION_COOKIE_SECURE is on. Make a new one with: "
            "python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    print(
        "WARNING: SECRET_KEY is shorter than 32 characters. Use a longer random "
        "key before putting this app online."
    )

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(qr_bp)
app.register_blueprint(qr_page_bp)

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

# Security headers on every response
@app.after_request
def add_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Content-Security-Policy', "frame-ancestors 'none'")
    response.headers.setdefault('Referrer-Policy', 'same-origin')

    if app.config['SESSION_COOKIE_SECURE']:
        response.headers.setdefault(
            'Strict-Transport-Security', 'max-age=31536000; includeSubDomains'
        )

    return response


# ============================================
# RUN THE APP
# ============================================
if __name__ == '__main__':
    app.run(debug=False, port=5000)
