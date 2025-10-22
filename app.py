#!/usr/bin/env python3
"""
Flask Web Application for Neurotec Voice Verification
Allows users to upload audio files and get VeriSpeak scores
"""

import os
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import logging
from neurotec_voice_verifier import NeurotecVoiceVerifier, VoiceVerificationResult

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Configure upload settings
UPLOAD_FOLDER = tempfile.mkdtemp(prefix='voice_uploads_')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Supported audio file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a', 'aac', 'ogg'}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_temp_files(*file_paths):
    """Clean up temporary files"""
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify_voices():
    """Handle voice verification request"""
    try:
        # Check if files were uploaded
        if 'reference_file' not in request.files or 'candidate_file' not in request.files:
            return jsonify({'error': 'Both reference and candidate files are required'}), 400
        
        ref_file = request.files['reference_file']
        cand_file = request.files['candidate_file']
        
        # Check if files were selected
        if ref_file.filename == '' or cand_file.filename == '':
            return jsonify({'error': 'Please select both files'}), 400
        
        # Validate file types
        if not (allowed_file(ref_file.filename) and allowed_file(cand_file.filename)):
            return jsonify({
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save uploaded files to temporary location
        ref_filename = secure_filename(ref_file.filename)
        cand_filename = secure_filename(cand_file.filename)
        
        ref_path = os.path.join(app.config['UPLOAD_FOLDER'], f"ref_{ref_filename}")
        cand_path = os.path.join(app.config['UPLOAD_FOLDER'], f"cand_{cand_filename}")
        
        ref_file.save(ref_path)
        cand_file.save(cand_path)
        
        logger.info(f"Files uploaded: {ref_filename} vs {cand_filename}")
        
        # Initialize verifier and perform verification
        verifier = NeurotecVoiceVerifier()
        result = verifier.verify_voices(ref_path, cand_path)
        
        # Clean up temporary files
        cleanup_temp_files(ref_path, cand_path)
        
        # Return results
        return jsonify({
            'success': result.success,
            'score': result.score,
            'threshold': result.threshold,
            'verification_status': result.verification_status,
            'far_percentage': result.far_percentage,
            'confidence_level': result.confidence_level,
            'reference_filename': ref_filename,
            'candidate_filename': cand_filename,
            'error_message': result.error_message
        })
        
    except Exception as e:
        logger.error(f"Error during verification: {e}")
        # Clean up files on error
        cleanup_temp_files(ref_path if 'ref_path' in locals() else None, 
                          cand_path if 'cand_path' in locals() else None)
        return jsonify({'error': str(e)}), 500

@app.route('/batch_verify', methods=['POST'])
def batch_verify():
    """Handle batch verification of multiple file pairs"""
    try:
        files = request.files.getlist('files')
        
        if len(files) < 2:
            return jsonify({'error': 'At least 2 files are required for batch processing'}), 400
        
        # Save all files
        file_paths = []
        filenames = []
        
        for file in files:
            if file.filename == '' or not allowed_file(file.filename):
                continue
                
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_paths.append(file_path)
            filenames.append(filename)
        
        if len(file_paths) < 2:
            return jsonify({'error': 'At least 2 valid audio files are required'}), 400
        
        # Create file pairs (first file as reference against all others)
        reference_file = file_paths[0]
        reference_name = filenames[0]
        
        file_pairs = [(reference_file, candidate_file) for candidate_file in file_paths[1:]]
        
        # Perform batch verification
        verifier = NeurotecVoiceVerifier()
        results = verifier.batch_verify(file_pairs)
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results):
            formatted_results.append({
                'reference_filename': reference_name,
                'candidate_filename': filenames[i + 1],
                'success': result.success,
                'score': result.score,
                'threshold': result.threshold,
                'verification_status': result.verification_status,
                'confidence_level': result.confidence_level,
                'error_message': result.error_message
            })
        
        # Clean up temporary files
        cleanup_temp_files(*file_paths)
        
        return jsonify({
            'success': True,
            'results': formatted_results,
            'total_pairs': len(file_pairs)
        })
        
    except Exception as e:
        logger.error(f"Error during batch verification: {e}")
        # Clean up files on error
        if 'file_paths' in locals():
            cleanup_temp_files(*file_paths)
        return jsonify({'error': str(e)}), 500

@app.route('/info')
def get_info():
    """Get SDK information"""
    try:
        verifier = NeurotecVoiceVerifier()
        info = verifier.get_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 50MB.'}), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error occurred'}), 500

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    logger.info(f"Upload directory: {UPLOAD_FOLDER}")
    
    # Run the application
    # host='0.0.0.0' allows access from other devices on local network
    app.run(debug=True, host='0.0.0.0', port=5000)