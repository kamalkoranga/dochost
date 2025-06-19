from datetime import datetime, timezone, timedelta
from flask import render_template, jsonify, send_from_directory, request, \
    current_app
from flask_login import current_user, login_required
import os
from app import db
import shutil
from app.main import bp
from app.utils import get_folder_size, get_user_upload_folder, create_user_folder


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
    BASE_USER_STORAGE = 5 * 1024 * 1024  # 5MB

    # Check subscription expiry
    now = datetime.now(timezone.utc)
    extra_mb = 0
    # Make subscription_expires_at timezone-aware before comparison
    expires_at = current_user.subscription_expires_at
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at and expires_at > now:
        extra_mb = getattr(current_user, "extra_storage_mb", 0) or 0
    MAX_USER_STORAGE = BASE_USER_STORAGE + (extra_mb * 1024 * 1024)

    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'error': 'No selected files'}), 400
    
    # Calculate current usage
    current_usage = get_folder_size(USER_FOLDER)
    # Calculate total size of new files
    new_files_total = sum(file.content_length or len(file.read()) for file in files)
    # Reset file pointer if .read() was used
    for file in files:
        file.stream.seek(0)
    
    if current_usage + new_files_total > MAX_USER_STORAGE:
        if extra_mb == 0:
            return jsonify({'error': 'Storage limit exceeded. Please subscribe to upload more files.'}), 400
        return jsonify({'error': f'Storage limit exceeded (Maximum {MAX_USER_STORAGE / (1024 * 1024)} MB)'}), 400

    for file in files:
        if file.filename == '':
            continue
            
        # Get the upload path from the form data
        upload_path = request.form.get(f'{file.filename}_path', file.filename)
        filepath = os.path.join(USER_FOLDER, upload_path)
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
    
    return jsonify({'message': 'File uploaded successfully'})

@bp.route('/files', methods=['GET'])
@bp.route('/files/<path:subpath>', methods=['GET'])
@login_required
def list_files(subpath=''):
    USER_FOLDER = get_user_upload_folder(current_user.username)
    target_folder = os.path.join(USER_FOLDER, subpath)
    if not os.path.exists(target_folder):
        create_user_folder(target_folder)
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
            return jsonify({'message': 'Folder deleted successfully'})
        else:
            os.remove(file_path)
            return jsonify({'message': 'File deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/pricing')
@login_required
def pricing():
    return render_template('pricing.html')


@bp.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({'error': 'No amount provided'}), 400

    amount = int(data['amount'])
    now = datetime.now(timezone.utc)
    duration = timedelta(minutes=1)  # 1 minute for testing

    # Determine new storage
    if amount == 2:
        new_extra_mb = 5
    elif amount == 4:
        new_extra_mb = 10
    else:
        return jsonify({'error': 'Invalid subscription amount'}), 400

    # Ensure subscription_expires_at is timezone-aware before comparison
    sub_exp = current_user.subscription_expires_at
    if sub_exp is not None and sub_exp.tzinfo is None:
        sub_exp = sub_exp.replace(tzinfo=timezone.utc)

    # If user already has a subscription
    if sub_exp and sub_exp > now:
        current_user.extra_storage_mb += new_extra_mb
        current_user.subscription_expires_at = sub_exp + duration
        # msg = f'Subscription extended! Extra storage: {current_user.extra_storage_mb} MB until {current_user.subscription_expires_at.strftime("%I:%M:%S %p, %d %B %Y")}'
        data = {
            'extra_storage_mb': current_user.extra_storage_mb,
            'subscription_expires_at': current_user.subscription_expires_at,
            'had_subscription': True
        }
    else:
        # New subscription
        current_user.extra_storage_mb = new_extra_mb
        current_user.subscription_expires_at = now + duration
        # msg = f'Subscription successful. Extra storage: {new_extra_mb} MB until {current_user.subscription_expires_at.strftime("%I:%M:%S %p, %d %B %Y")}'
        data = {
            'extra_storage_mb': new_extra_mb,
            'subscription_expires_at': current_user.subscription_expires_at,
            'had_subscription': False
        }

    db.session.commit()
    return jsonify({'data': data})

@bp.route('/storage-info', methods=['GET'])
@login_required
def storage_info():
    BASE_USER_STORAGE = 5 * 1024 * 1024  # 5MB per user
    now = datetime.now(timezone.utc)
    extra_mb = 0
    expires_at = None

    sub_exp = current_user.subscription_expires_at
    # Ensure sub_exp is timezone-aware before comparison
    if sub_exp is not None:
        if sub_exp.tzinfo is None:
            sub_exp = sub_exp.replace(tzinfo=timezone.utc)
        if sub_exp > now:
            extra_mb = getattr(current_user, "extra_storage_mb", 0) or 0
            expires_at = sub_exp

    MAX_USER_STORAGE = BASE_USER_STORAGE + (extra_mb * 1024 * 1024)
    used = get_folder_size(get_user_upload_folder(current_user.username))
    free = MAX_USER_STORAGE - used if used < MAX_USER_STORAGE else 0
    return jsonify({
        'total': MAX_USER_STORAGE,
        'used': used,
        'free': free,
        'subscription_expires_at': expires_at.isoformat() if expires_at else None
    })
