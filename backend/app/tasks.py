from . import celery, db
from .models import Reminder, Task, Plan, User
from .services.gpt_handler import GPTHandler
from flask_mail import Message
from . import mail
from datetime import datetime, timedelta
import json

@celery.task
def process_reminders():
    """Process scheduled reminders"""
    try:
        # Get reminders that should fire now
        active_reminders = Reminder.query.filter(
            Reminder.is_active == True,
            Reminder.next_fire_at <= datetime.utcnow()
        ).all()
        
        for reminder in active_reminders:
            # Send reminder (in a real app, this would be email/push notification)
            print(f"Reminder for user {reminder.user_id}: {reminder.title}")
            
            # For now, just advance the tier
            if not reminder.advance_tier():
                reminder.is_active = False
        
        db.session.commit()
        return f"Processed {len(active_reminders)} reminders"
        
    except Exception as e:
        db.session.rollback()
        return f"Error processing reminders: {str(e)}"

@celery.task
def send_reminder_email(user_id, reminder_id):
    """Send reminder email to user"""
    try:
        user = User.query.get(user_id)
        reminder = Reminder.query.get(reminder_id)
        
        if not user or not reminder:
            return "User or reminder not found"
        
        msg = Message(
            subject=f"Study Reminder: {reminder.title}",
            recipients=[user.email],
            body=f"""
            Hi {user.email},
            
            This is a reminder for your study session:
            
            {reminder.title}
            {reminder.content}
            
            Keep up the great work!
            
            Best regards,
            Your Personal Learning Assistant
            """
        )
        
        mail.send(msg)
        return f"Reminder email sent to {user.email}"
        
    except Exception as e:
        return f"Error sending reminder email: {str(e)}"

@celery.task
def generate_daily_insights(user_id):
    """Generate daily insights for user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
        # Get today's tasks
        today = datetime.now().date()
        today_tasks = Task.query.join(Plan).filter(
            Plan.user_id == user_id,
            Task.date == today
        ).all()
        
        if not today_tasks:
            return "No tasks for today"
        
        # Generate insights using GPT
        gpt_handler = GPTHandler()
        
        task_summary = "\n".join([f"- {task.title}" for task in today_tasks])
        
        insight_prompt = f"""
        Based on these study tasks for today:
        {task_summary}
        
        Provide a brief, encouraging insight or tip (max 100 words) to help the student stay motivated.
        """
        
        insight = gpt_handler.chat_response(insight_prompt, [], f"User is a {user.persona}.")
        
        # Create a reminder with the insight
        reminder = Reminder(
            user_id=user_id,
            title="Daily Study Insight",
            content=insight,
            tier=1
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        return f"Generated daily insight for user {user_id}"
        
    except Exception as e:
        db.session.rollback()
        return f"Error generating daily insights: {str(e)}"

@celery.task
def cleanup_old_data():
    """Clean up old data to maintain performance"""
    try:
        # Remove old chat logs (older than 90 days)
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        old_chat_logs = ChatLog.query.filter(ChatLog.timestamp < cutoff_date).delete()
        
        # Remove old reminders (older than 30 days and inactive)
        old_reminders = Reminder.query.filter(
            Reminder.is_active == False,
            Reminder.updated_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        return f"Cleaned up {old_chat_logs} chat logs and {old_reminders} reminders"
        
    except Exception as e:
        db.session.rollback()
        return f"Error cleaning up old data: {str(e)}"

@celery.task
def analyze_study_patterns(user_id):
    """Analyze user's study patterns and suggest improvements"""
    try:
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
        # Get recent study data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Analyze task completion patterns
        daily_completions = db.session.query(
            Task.date,
            db.func.count(Task.id).label('total'),
            db.func.sum(db.case([(Task.status == 'completed', 1)], else_=0)).label('completed')
        ).join(Plan).filter(
            Plan.user_id == user_id,
            Task.date >= start_date,
            Task.date <= end_date
        ).group_by(Task.date).all()
        
        if not daily_completions:
            return "No study data to analyze"
        
        # Calculate patterns
        completion_rates = [day.completed / day.total if day.total > 0 else 0 for day in daily_completions]
        avg_completion_rate = sum(completion_rates) / len(completion_rates)
        
        # Generate personalized suggestions
        gpt_handler = GPTHandler()
        
        if avg_completion_rate < 0.5:
            suggestion = "Consider breaking down larger tasks into smaller, more manageable chunks."
        elif avg_completion_rate < 0.8:
            suggestion = "You're doing well! Try setting specific time blocks for studying to improve consistency."
        else:
            suggestion = "Excellent work! Consider challenging yourself with more advanced topics."
        
        # Create a reminder with the suggestion
        reminder = Reminder(
            user_id=user_id,
            title="Study Pattern Analysis",
            content=f"Based on your recent study patterns, here's a suggestion: {suggestion}",
            tier=2
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        return f"Analyzed study patterns for user {user_id}"
        
    except Exception as e:
        db.session.rollback()
        return f"Error analyzing study patterns: {str(e)}" 