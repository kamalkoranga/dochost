from datetime import datetime, timezone
from flask import render_template, jsonify, send_from_directory, request, \
    current_app
from flask_login import current_user, login_required
import os
from app import db
import shutil
from app.main import bp
from app.utils import get_folder_size, get_user_upload_folder


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@bp.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.username)


@bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    USER_FOLDER = get_user_upload_folder(current_user.username)

    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'error': 'No selected files'}), 400
    
    for file in files:
        if file.filename == '':
            continue
            
        # Get the upload path from the form data
        upload_path = request.form.get(f'{file.filename}_path', file.filename)
        filepath = os.path.join(USER_FOLDER, upload_path)
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
    
    return jsonify({'message': 'Files uploaded successfully'})

@bp.route('/files', methods=['GET'])
@bp.route('/files/<path:subpath>', methods=['GET'])
@login_required
def list_files(subpath=''):
    USER_FOLDER = get_user_upload_folder(current_user.username)
    target_folder = os.path.join(USER_FOLDER, subpath)
    if not os.path.exists(target_folder):
        return jsonify({'error': 'Path not found'}), 404
    
    items = []
    for item in os.listdir(target_folder):
        full_path = os.path.join(target_folder, item)
        rel_path = os.path.join(subpath, item)
        is_dir = os.path.isdir(full_path)
        size = get_folder_size(full_path) if is_dir else os.path.getsize(full_path)

        thumbnail = None
        if is_dir:
            base_name = os.path.splitext(item)[0]
            for ext in ['.jpg', '.jpeg', '.png']:
                thumb_path = os.path.join(target_folder, f"{base_name}\\{base_name}{ext}")
                if os.path.exists(thumb_path):
                    thumbnail = f"{rel_path.rsplit('.', 1)[0]}{ext}"
                    thumbnail = thumb_path
                    break

        items.append({
            'name': "🎞️" + item if '.mp4' in item else "📄" + item if is_dir == False else ''+item,
            'path': rel_path,
            'is_dir': is_dir,
            'size': size,
            'thumbnail': thumbnail
        })
    
    return jsonify({'files': items})


@bp.route('/download/<path:filename>', methods=['GET'])
@login_required
def download_file(filename):
    USER_FOLDER = get_user_upload_folder(current_user.username)
    directory = os.path.dirname(os.path.join(USER_FOLDER, filename))
    file = os.path.basename(filename)
    return send_from_directory(directory, file, as_attachment=True)


@bp.route('/create-folder', methods=['POST'])
@login_required
def create_folder():
    USER_FOLDER = get_user_upload_folder(current_user.username)

    data = request.get_json()
    if not data or 'folderName' not in data:
        return jsonify({'error': 'No folder name provided'}), 400
    
    folder_path = os.path.join(USER_FOLDER, data['folderName'])
    try:
        os.makedirs(folder_path, exist_ok=True)
        return jsonify({'message': 'Folder created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/delete/<path:filename>', methods=['DELETE'])
@login_required
def delete_file(filename):
    UPLOAD_FOLDER = get_user_upload_folder(current_user.username)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    try:
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
        return jsonify({'message': 'Item deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/storage-info', methods=['GET'])
@login_required
def storage_info():
    total, used, free = shutil.disk_usage(current_app.config['UPLOAD_FOLDER'])  # or just "/"
    return jsonify({
        'total': total,
        'used': used,
        'free': free
    })
