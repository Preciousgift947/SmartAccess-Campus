from flask import Flask
from config import Config
from routes.auth import auth_bp
from routes.student import student_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)

# ============================================
# RUN THE APP
# ============================================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
