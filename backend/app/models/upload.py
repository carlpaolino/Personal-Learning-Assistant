from .. import db
from datetime import datetime
import json

class Upload(db.Model):
    __tablename__ = 'uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, docx
    file_size = db.Column(db.Integer, nullable=False)
    parsed_json = db.Column(db.Text)  # Extracted Q/A pairs and concepts
    status = db.Column(db.String(20), default='uploaded')  # uploaded, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, filename, file_url, file_type, file_size):
        self.user_id = user_id
        self.filename = filename
        self.file_url = file_url
        self.file_type = file_type
        self.file_size = file_size
    
    def get_parsed_data(self):
        """Get parsed data as dict"""
        try:
            return json.loads(self.parsed_json) if self.parsed_json else {}
        except:
            return {}
    
    def set_parsed_data(self, data):
        """Set parsed data"""
        self.parsed_json = json.dumps(data)
        self.status = 'completed'
    
    def to_dict(self):
        """Convert upload to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'parsed_data': self.get_parsed_data(),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Upload {self.filename}>' 