import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()

# Create the app
app = Flask(__name__)
# It's important to set a secure secret key in a production environment
app.secret_key = os.environ.get("SESSION_SECRET", "a-secure-development-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database to use a simple SQLite file
# For Vercel, use /tmp directory which is writable
if os.environ.get("VERCEL"):
    db_path = "/tmp/astrology_app.db"
    upload_path = "/tmp/uploads"
else:
    db_path = "astrology_app.db"
    upload_path = os.path.join(os.getcwd(), 'static', 'uploads')

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{db_path}")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure file uploads
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size for all uploads
app.config['UPLOAD_FOLDER'] = upload_path

# Ensure the upload directory exists
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except Exception as e:
    logging.warning(f"Could not create upload directory: {e}")

# Initialize extensions
db.init_app(app)
csrf.init_app(app)

# Import routes after app creation to avoid circular imports
try:
    from routes import *
except ImportError as e:
    logging.error(f"Error importing routes: {e}")
    raise

# Create database tables within the application context
try:
    with app.app_context():
        # Import models to ensure their tables are created
        import models
        db.create_all()
except Exception as e:
    logging.error(f"Error creating database tables: {e}")
    # Don't raise - allow app to start even if DB creation fails

if __name__ == '__main__':
    # Running in debug mode is not recommended for production
    app.run(host='0.0.0.0', port=5000, debug=True)
