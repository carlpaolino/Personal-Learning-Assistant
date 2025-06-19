from .. import db
from datetime import datetime, timedelta

class Reminder(db.Model):
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tier = db.Column(db.Integer, default=1)  # 1-4 for spaced repetition tiers
    next_fire_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, title, content, tier=1, task_id=None):
        self.user_id = user_id
        self.title = title
        self.content = content
        self.tier = tier
        self.task_id = task_id
        self.next_fire_at = self._calculate_next_fire()
    
    def _calculate_next_fire(self):
        """Calculate next fire time based on tier"""
        now = datetime.utcnow()
        if self.tier == 1:
            return now + timedelta(days=1)  # 0-2 days
        elif self.tier == 2:
            return now + timedelta(days=4)  # 3-5 days
        elif self.tier == 3:
            return now + timedelta(days=10)  # 7-14 days
        elif self.tier == 4:
            return now + timedelta(days=30)  # 30+ days
        else:
            return now + timedelta(days=1)
    
    def advance_tier(self):
        """Advance to next tier and recalculate fire time"""
        if self.tier < 4:
            self.tier += 1
            self.next_fire_at = self._calculate_next_fire()
            return True
        return False
    
    def to_dict(self):
        """Convert reminder to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'title': self.title,
            'content': self.content,
            'tier': self.tier,
            'next_fire_at': self.next_fire_at.isoformat(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Reminder {self.title}>' 