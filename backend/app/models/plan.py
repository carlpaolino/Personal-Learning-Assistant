from .. import db
from datetime import datetime
import json

class Plan(db.Model):
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    topics = db.Column(db.Text, nullable=False)  # JSON string of topics
    start_date = db.Column(db.Date, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    json_blob = db.Column(db.Text)  # Complete plan data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='plan', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id, title, topics, start_date, target_date, json_blob=None):
        self.user_id = user_id
        self.title = title
        self.topics = json.dumps(topics) if isinstance(topics, list) else topics
        self.start_date = start_date
        self.target_date = target_date
        self.json_blob = json_blob
    
    def get_topics(self):
        """Get topics as list"""
        try:
            return json.loads(self.topics)
        except:
            return []
    
    def get_plan_data(self):
        """Get plan data as dict"""
        try:
            return json.loads(self.json_blob) if self.json_blob else {}
        except:
            return {}
    
    def to_dict(self):
        """Convert plan to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'topics': self.get_topics(),
            'start_date': self.start_date.isoformat(),
            'target_date': self.target_date.isoformat(),
            'plan_data': self.get_plan_data(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tasks': [task.to_dict() for task in self.tasks]
        }
    
    def __repr__(self):
        return f'<Plan {self.title}>'

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, completed, skipped
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, plan_id, date, title, description=None, order_index=0):
        self.plan_id = plan_id
        self.date = date
        self.title = title
        self.description = description
        self.order_index = order_index
    
    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'date': self.date.isoformat(),
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Task {self.title}>' 