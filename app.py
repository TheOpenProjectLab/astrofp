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
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///astrology_app.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure file uploads
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size for all uploads
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
csrf.init_app(app)

# Import routes after app creation to avoid circular imports
from routes import *

# Create database tables within the application context
with app.app_context():
    # Import models to ensure their tables are created
    import models
    db.create_all()

# Vercel serverless function handler
# This is required for Vercel deployment
def handler(request):
    return app(request.environ, request.start_response)

if __name__ == '__main__':
    # Running in debug mode is not recommended for production
    app.run(host='0.0.0.0', port=5000, debug=True)
