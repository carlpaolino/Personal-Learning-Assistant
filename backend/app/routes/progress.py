from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Plan, Task, Upload, ChatLog
from .. import db
from datetime import datetime, timedelta
from sqlalchemy import func, and_

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get user dashboard data"""
    try:
        user_id = get_jwt_identity()
        
        # Get date range (last 30 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Plan adherence
        total_tasks = Task.query.join(Plan).filter(
            Plan.user_id == user_id,
            Task.date >= start_date,
            Task.date <= end_date
        ).count()
        
        completed_tasks = Task.query.join(Plan).filter(
            Plan.user_id == user_id,
            Task.date >= start_date,
            Task.date <= end_date,
            Task.status == 'completed'
        ).count()
        
        adherence_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Topics mastered (plans with high completion rate)
        plans = Plan.query.filter_by(user_id=user_id).all()
        mastered_topics = []
        
        for plan in plans:
            plan_tasks = Task.query.filter_by(plan_id=plan.id).all()
            if plan_tasks:
                completion_rate = sum(1 for task in plan_tasks if task.status == 'completed') / len(plan_tasks)
                if completion_rate >= 0.8:  # 80% completion rate
                    mastered_topics.extend(plan.get_topics())
        
        # Time spent (estimated based on task completion)
        estimated_time = completed_tasks * 45  # 45 minutes per task
        
        # Efficiency score (combination of adherence and consistency)
        consistency_score = self._calculate_consistency_score(user_id, start_date, end_date)
        efficiency_score = (adherence_rate * 0.7) + (consistency_score * 0.3)
        
        # Recent activity
        recent_plans = Plan.query.filter_by(user_id=user_id).order_by(Plan.created_at.desc()).limit(5).all()
        recent_uploads = Upload.query.filter_by(user_id=user_id).order_by(Upload.created_at.desc()).limit(5).all()
        
        return jsonify({
            'dashboard': {
                'plan_adherence': round(adherence_rate, 1),
                'topics_mastered': len(set(mastered_topics)),
                'time_spent_minutes': estimated_time,
                'efficiency_score': round(efficiency_score, 1),
                'total_plans': len(plans),
                'total_uploads': Upload.query.filter_by(user_id=user_id).count(),
                'recent_plans': [plan.to_dict() for plan in recent_plans],
                'recent_uploads': [upload.to_dict() for upload in recent_uploads]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard data', 'details': str(e)}), 500

@progress_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get detailed analytics"""
    try:
        user_id = get_jwt_identity()
        
        # Get date range from query params
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Daily task completion
        daily_completions = db.session.query(
            Task.date,
            func.count(Task.id).label('total'),
            func.sum(func.case([(Task.status == 'completed', 1)], else_=0)).label('completed')
        ).join(Plan).filter(
            Plan.user_id == user_id,
            Task.date >= start_date,
            Task.date <= end_date
        ).group_by(Task.date).all()
        
        # Topic breakdown
        topic_stats = {}
        plans = Plan.query.filter_by(user_id=user_id).all()
        
        for plan in plans:
            for topic in plan.get_topics():
                if topic not in topic_stats:
                    topic_stats[topic] = {'total_tasks': 0, 'completed_tasks': 0}
                
                plan_tasks = Task.query.filter_by(plan_id=plan.id).all()
                topic_stats[topic]['total_tasks'] += len(plan_tasks)
                topic_stats[topic]['completed_tasks'] += sum(1 for task in plan_tasks if task.status == 'completed')
        
        # Chat activity
        chat_sessions = ChatLog.query.filter_by(user_id=user_id).count()
        
        return jsonify({
            'analytics': {
                'daily_completions': [
                    {
                        'date': str(day.date),
                        'total': day.total,
                        'completed': day.completed,
                        'rate': round((day.completed / day.total * 100) if day.total > 0 else 0, 1)
                    }
                    for day in daily_completions
                ],
                'topic_stats': [
                    {
                        'topic': topic,
                        'total_tasks': stats['total_tasks'],
                        'completed_tasks': stats['completed_tasks'],
                        'completion_rate': round((stats['completed_tasks'] / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0, 1)
                    }
                    for topic, stats in topic_stats.items()
                ],
                'chat_activity': {
                    'total_sessions': chat_sessions,
                    'avg_messages_per_session': self._calculate_avg_messages_per_session(user_id)
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get analytics', 'details': str(e)}), 500

@progress_bp.route('/reminders', methods=['GET'])
@jwt_required()
def get_reminders():
    """Get active reminders for user"""
    try:
        user_id = get_jwt_identity()
        
        from ..models import Reminder
        
        # Get active reminders
        reminders = Reminder.query.filter(
            Reminder.user_id == user_id,
            Reminder.is_active == True,
            Reminder.next_fire_at <= datetime.utcnow()
        ).order_by(Reminder.next_fire_at.asc()).all()
        
        return jsonify({
            'reminders': [reminder.to_dict() for reminder in reminders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get reminders', 'details': str(e)}), 500

@progress_bp.route('/reminders/<int:reminder_id>/dismiss', methods=['POST'])
@jwt_required()
def dismiss_reminder(reminder_id):
    """Dismiss a reminder"""
    try:
        user_id = get_jwt_identity()
        
        from ..models import Reminder
        
        reminder = Reminder.query.filter_by(id=reminder_id, user_id=user_id).first()
        
        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404
        
        # Advance to next tier or deactivate
        if not reminder.advance_tier():
            reminder.is_active = False
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reminder dismissed successfully',
            'reminder': reminder.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to dismiss reminder', 'details': str(e)}), 500

def _calculate_consistency_score(self, user_id, start_date, end_date):
    """Calculate consistency score based on daily activity"""
    try:
        # Get daily task counts
        daily_tasks = db.session.query(
            Task.date,
            func.count(Task.id).label('task_count')
        ).join(Plan).filter(
            Plan.user_id == user_id,
            Task.date >= start_date,
            Task.date <= end_date
        ).group_by(Task.date).all()
        
        if not daily_tasks:
            return 0
        
        # Calculate consistency (lower variance = higher consistency)
        task_counts = [day.task_count for day in daily_tasks]
        mean_count = sum(task_counts) / len(task_counts)
        
        if mean_count == 0:
            return 0
        
        variance = sum((count - mean_count) ** 2 for count in task_counts) / len(task_counts)
        consistency = max(0, 100 - (variance * 10))  # Scale variance to 0-100
        
        return min(100, consistency)
        
    except Exception:
        return 0

def _calculate_avg_messages_per_session(self, user_id):
    """Calculate average messages per chat session"""
    try:
        from sqlalchemy import func
        
        # Get session counts
        session_counts = db.session.query(
            ChatLog.session_id,
            func.count(ChatLog.id).label('message_count')
        ).filter_by(user_id=user_id).group_by(ChatLog.session_id).all()
        
        if not session_counts:
            return 0
        
        total_messages = sum(session.message_count for session in session_counts)
        avg_messages = total_messages / len(session_counts)
        
        return round(avg_messages, 1)
        
    except Exception:
        return 0 