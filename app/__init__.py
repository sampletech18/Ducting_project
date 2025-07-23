from flask import Flask
from .models import db
import os

def create_app():
    app = Flask(__name__)

    # ✅ Get DB URL from environment or fallback to local SQLite
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///ducting.db')

    # ✅ Convert postgres:// to postgresql:// if needed (Render uses old format)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ✅ Register blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.project import project_bp
    from .routes.seed import seed_bp
    from .routes.measurement import measurement_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(seed_bp)
    app.register_blueprint(measurement_bp)

    return app
