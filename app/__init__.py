from flask import Flask
from .extensions import db, jwt
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register blueprints (routes)
    from .routes import auth, student, qr
    app.register_blueprint(auth.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(qr.bp)

    return app