from app import db
from datetime import datetime
import uuid

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Personal Details
    title = db.Column(db.String(10))
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    # Submission details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.Text)
    
    # Relationships
    fingerprints = db.relationship('Fingerprint', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Client {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        name_parts = [self.title, self.first_name, self.middle_name, self.last_name]
        return ' '.join(part for part in name_parts if part)

class Fingerprint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    finger_position = db.Column(db.String(5), nullable=False)  # L1-L5, R1-R5
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Fingerprint {self.finger_position} for Client {self.client_id}>'
