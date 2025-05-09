from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
import os
import shutil
from dotenv import load_dotenv
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1440)
UPLOAD_FOLDER = os.environ.get('DRIVE_PATH')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

users = {
    "john": generate_password_hash("hello"),
    "susan": generate_password_hash("bye")
}

# Custom login_required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_folder_size(path):
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_folder_size(entry.path)
    return total


@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and check_password_hash(users.get(username), password):
            session['username'] = username
            session.permanent = True
            return redirect(url_for('index'))

        return render_template('login.html', error="Invalid credentials")

    if 'username' in session:
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
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
        filepath = os.path.join(UPLOAD_FOLDER, upload_path)
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
    
    return jsonify({'message': 'Files uploaded successfully'})


@app.route('/files', methods=['GET'])
@app.route('/files/<path:subpath>', methods=['GET'])
@login_required
def list_files(subpath=''):
    target_folder = os.path.join(UPLOAD_FOLDER, subpath)
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


@app.route('/download/<path:filename>', methods=['GET'])
@login_required
def download_file(filename):
    directory = os.path.dirname(os.path.join(UPLOAD_FOLDER, filename))
    file = os.path.basename(filename)
    return send_from_directory(directory, file, as_attachment=True)


@app.route('/create-folder', methods=['POST'])
@login_required
def create_folder():
    data = request.get_json()
    if not data or 'folderName' not in data:
        return jsonify({'error': 'No folder name provided'}), 400
    
    folder_path = os.path.join(UPLOAD_FOLDER, data['folderName'])
    try:
        os.makedirs(folder_path, exist_ok=True)
        return jsonify({'message': 'Folder created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete/<path:filename>', methods=['DELETE'])
@login_required
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    try:
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
        return jsonify({'message': 'Item deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/storage-info', methods=['GET'])
@login_required
def storage_info():
    total, used, free = shutil.disk_usage("drive")  # or just "/"
    return jsonify({
        'total': total,
        'used': used,
        'free': free
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
