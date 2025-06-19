from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import ChatLog, User
from ..services.gpt_handler import GPTHandler
from .. import db
import uuid
from datetime import datetime

ai_bp = Blueprint('ai', __name__)
gpt_handler = GPTHandler()

@ai_bp.route('/explain', methods=['POST'])
@jwt_required()
def explain_topic():
    """Get AI explanation for a topic"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('topic'):
            return jsonify({'error': 'Topic is required'}), 400
        
        topic = data['topic']
        persona_level = data.get('persona_level', 'student')
        max_words = data.get('max_words', 500)
        
        # Get user persona if not specified
        if persona_level == 'auto':
            user = User.query.get(user_id)
            persona_level = user.persona if user else 'student'
        
        # Generate explanation
        explanation = gpt_handler.explain_topic(topic, persona_level, max_words)
        
        return jsonify({
            'topic': topic,
            'explanation': explanation,
            'persona_level': persona_level
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate explanation', 'details': str(e)}), 500

@ai_bp.route('/quiz', methods=['POST'])
@jwt_required()
def generate_quiz():
    """Generate quiz questions for a topic"""
    try:
        data = request.get_json()
        
        if not data or not data.get('topic'):
            return jsonify({'error': 'Topic is required'}), 400
        
        topic = data['topic']
        num_questions = data.get('num_questions', 5)
        
        # Generate quiz
        questions = gpt_handler.generate_quiz(topic, num_questions)
        
        return jsonify({
            'topic': topic,
            'questions': questions,
            'total_questions': len(questions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate quiz', 'details': str(e)}), 500

@ai_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """Chat with AI tutor"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        session_id = data.get('session_id')
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get chat history for this session (last 10 messages)
        chat_history = ChatLog.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).order_by(ChatLog.timestamp.desc()).limit(10).all()
        
        # Convert to format expected by GPT handler
        history = []
        for chat in reversed(chat_history):  # Reverse to get chronological order
            history.append({
                'role': chat.role,
                'content': chat.content
            })
        
        # Get user context for AI
        user = User.query.get(user_id)
        user_context = f"User is a {user.persona if user else 'student'}."
        
        # Generate AI response
        response = gpt_handler.chat_response(message, history, user_context)
        
        # Save user message
        user_chat = ChatLog(
            user_id=user_id,
            session_id=session_id,
            role='user',
            content=message
        )
        db.session.add(user_chat)
        
        # Save AI response
        ai_chat = ChatLog(
            user_id=user_id,
            session_id=session_id,
            role='assistant',
            content=response
        )
        db.session.add(ai_chat)
        
        db.session.commit()
        
        return jsonify({
            'session_id': session_id,
            'response': response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to process chat', 'details': str(e)}), 500

@ai_bp.route('/chat/history/<session_id>', methods=['GET'])
@jwt_required()
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        user_id = get_jwt_identity()
        
        # Get chat history
        chat_logs = ChatLog.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).order_by(ChatLog.timestamp.asc()).all()
        
        return jsonify({
            'session_id': session_id,
            'messages': [chat.to_dict() for chat in chat_logs]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get chat history', 'details': str(e)}), 500

@ai_bp.route('/chat/sessions', methods=['GET'])
@jwt_required()
def get_chat_sessions():
    """Get all chat sessions for user"""
    try:
        user_id = get_jwt_identity()
        
        # Get unique session IDs with latest message
        from sqlalchemy import func
        sessions = db.session.query(
            ChatLog.session_id,
            func.max(ChatLog.timestamp).label('last_message')
        ).filter_by(user_id=user_id).group_by(ChatLog.session_id).order_by(
            func.max(ChatLog.timestamp).desc()
        ).all()
        
        return jsonify({
            'sessions': [
                {
                    'session_id': session.session_id,
                    'last_message': session.last_message.isoformat()
                }
                for session in sessions
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get chat sessions', 'details': str(e)}), 500 