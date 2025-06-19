from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Plan, Task, User
from ..services.gpt_handler import GPTHandler
from .. import db
from datetime import datetime, date
import json

planner_bp = Blueprint('planner', __name__)
gpt_handler = GPTHandler()

@planner_bp.route('/create', methods=['POST'])
@jwt_required()
def create_plan():
    """Create a new study plan"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('topics') or not data.get('target_date'):
            return jsonify({'error': 'Topics and target date are required'}), 400
        
        topics = data['topics']
        target_date_str = data['target_date']
        title = data.get('title', f'Study Plan for {", ".join(topics)}')
        
        # Validate topics
        if not isinstance(topics, list) or len(topics) == 0:
            return jsonify({'error': 'Topics must be a non-empty list'}), 400
        
        # Parse target date
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid target date format. Use YYYY-MM-DD'}), 400
        
        # Get user persona for AI planning
        user = User.query.get(user_id)
        persona = user.persona if user else 'student'
        
        # Generate AI study plan
        start_date = date.today()
        ai_plan = gpt_handler.create_study_plan(topics, target_date_str, persona)
        
        # Create plan in database
        plan = Plan(
            user_id=user_id,
            title=title,
            topics=topics,
            start_date=start_date,
            target_date=target_date,
            json_blob=json.dumps(ai_plan)
        )
        
        db.session.add(plan)
        db.session.flush()  # Get plan ID
        
        # Create tasks from AI plan
        for day_data in ai_plan.get('daily_tasks', []):
            day_date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
            
            for i, task_data in enumerate(day_data.get('tasks', [])):
                task = Task(
                    plan_id=plan.id,
                    date=day_date,
                    title=task_data['title'],
                    description=task_data.get('description', ''),
                    order_index=i
                )
                db.session.add(task)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Study plan created successfully',
            'plan': plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create plan', 'details': str(e)}), 500

@planner_bp.route('/plans', methods=['GET'])
@jwt_required()
def get_plans():
    """Get all plans for current user"""
    try:
        user_id = get_jwt_identity()
        plans = Plan.query.filter_by(user_id=user_id).order_by(Plan.created_at.desc()).all()
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get plans', 'details': str(e)}), 500

@planner_bp.route('/plans/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_plan(plan_id):
    """Get specific plan by ID"""
    try:
        user_id = get_jwt_identity()
        plan = Plan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        return jsonify({
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get plan', 'details': str(e)}), 500

@planner_bp.route('/plans/<int:plan_id>/tasks/<date>', methods=['GET'])
@jwt_required()
def get_tasks_for_date(plan_id, date):
    """Get tasks for a specific date"""
    try:
        user_id = get_jwt_identity()
        
        # Verify plan belongs to user
        plan = Plan.query.filter_by(id=plan_id, user_id=user_id).first()
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        # Parse date
        try:
            task_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get tasks for date
        tasks = Task.query.filter_by(plan_id=plan_id, date=task_date).order_by(Task.order_index).all()
        
        return jsonify({
            'date': date,
            'tasks': [task.to_dict() for task in tasks]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get tasks', 'details': str(e)}), 500

@planner_bp.route('/tasks/<int:task_id>', methods=['PATCH'])
@jwt_required()
def update_task(task_id):
    """Update task status"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get task and verify ownership
        task = Task.query.join(Plan).filter(
            Task.id == task_id,
            Plan.user_id == user_id
        ).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Update allowed fields
        if 'status' in data:
            if data['status'] not in ['pending', 'completed', 'skipped']:
                return jsonify({'error': 'Invalid status'}), 400
            task.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update task', 'details': str(e)}), 500

@planner_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_plan(plan_id):
    """Delete a plan"""
    try:
        user_id = get_jwt_identity()
        plan = Plan.query.filter_by(id=plan_id, user_id=user_id).first()
        
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        db.session.delete(plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Plan deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete plan', 'details': str(e)}), 500 