from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from ..models import Upload
from ..services.file_parser import FileParser
from .. import db
import os
import uuid
from datetime import datetime

uploads_bp = Blueprint('uploads', __name__)
file_parser = FileParser()

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@uploads_bp.route('/exam', methods=['POST'])
@jwt_required()
def upload_exam():
    """Upload exam file and parse for Q/A pairs"""
    try:
        user_id = get_jwt_identity()
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': 'Unsupported file type. Only PDF and DOCX files are allowed.'}), 400
        
        # Secure filename and create unique path
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Validate file size and type
        validation = file_parser.validate_file(file_path)
        if not validation['valid']:
            os.remove(file_path)  # Clean up
            return jsonify({'error': validation['error']}), 400
        
        # Create upload record
        upload = Upload(
            user_id=user_id,
            filename=filename,
            file_url=file_path,
            file_type=file_extension,
            file_size=validation['file_size'],
            status='uploaded'
        )
        
        db.session.add(upload)
        db.session.flush()  # Get upload ID
        
        # Parse file content
        try:
            if file_extension == 'pdf':
                parsed_data = file_parser.parse_pdf(file_path)
            else:  # docx
                parsed_data = file_parser.parse_docx(file_path)
            
            # Update upload with parsed data
            upload.set_parsed_data(parsed_data)
            
            db.session.commit()
            
            return jsonify({
                'message': 'File uploaded and parsed successfully',
                'upload': upload.to_dict()
            }), 201
            
        except Exception as parse_error:
            # If parsing fails, still save the upload but mark as failed
            upload.status = 'failed'
            db.session.commit()
            
            return jsonify({
                'message': 'File uploaded but parsing failed',
                'upload': upload.to_dict(),
                'parse_error': str(parse_error)
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to upload file', 'details': str(e)}), 500

@uploads_bp.route('/uploads', methods=['GET'])
@jwt_required()
def get_uploads():
    """Get all uploads for current user"""
    try:
        user_id = get_jwt_identity()
        uploads = Upload.query.filter_by(user_id=user_id).order_by(Upload.created_at.desc()).all()
        
        return jsonify({
            'uploads': [upload.to_dict() for upload in uploads]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get uploads', 'details': str(e)}), 500

@uploads_bp.route('/uploads/<int:upload_id>', methods=['GET'])
@jwt_required()
def get_upload(upload_id):
    """Get specific upload by ID"""
    try:
        user_id = get_jwt_identity()
        upload = Upload.query.filter_by(id=upload_id, user_id=user_id).first()
        
        if not upload:
            return jsonify({'error': 'Upload not found'}), 404
        
        return jsonify({
            'upload': upload.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get upload', 'details': str(e)}), 500

@uploads_bp.route('/uploads/<int:upload_id>', methods=['DELETE'])
@jwt_required()
def delete_upload(upload_id):
    """Delete an upload"""
    try:
        user_id = get_jwt_identity()
        upload = Upload.query.filter_by(id=upload_id, user_id=user_id).first()
        
        if not upload:
            return jsonify({'error': 'Upload not found'}), 404
        
        # Delete file from filesystem
        try:
            if os.path.exists(upload.file_url):
                os.remove(upload.file_url)
        except Exception as file_error:
            # Log file deletion error but continue with database deletion
            print(f"Error deleting file {upload.file_url}: {file_error}")
        
        # Delete from database
        db.session.delete(upload)
        db.session.commit()
        
        return jsonify({
            'message': 'Upload deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete upload', 'details': str(e)}), 500

@uploads_bp.route('/uploads/<int:upload_id>/reparse', methods=['POST'])
@jwt_required()
def reparse_upload(upload_id):
    """Reparse an uploaded file"""
    try:
        user_id = get_jwt_identity()
        upload = Upload.query.filter_by(id=upload_id, user_id=user_id).first()
        
        if not upload:
            return jsonify({'error': 'Upload not found'}), 404
        
        if not os.path.exists(upload.file_url):
            return jsonify({'error': 'File not found on disk'}), 404
        
        # Reparse file
        try:
            if upload.file_type == 'pdf':
                parsed_data = file_parser.parse_pdf(upload.file_url)
            else:  # docx
                parsed_data = file_parser.parse_docx(upload.file_url)
            
            # Update upload with new parsed data
            upload.set_parsed_data(parsed_data)
            db.session.commit()
            
            return jsonify({
                'message': 'File reparsed successfully',
                'upload': upload.to_dict()
            }), 200
            
        except Exception as parse_error:
            upload.status = 'failed'
            db.session.commit()
            
            return jsonify({
                'error': 'Failed to reparse file',
                'details': str(parse_error)
            }), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reparse upload', 'details': str(e)}), 500 