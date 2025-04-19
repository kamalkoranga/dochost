from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import shutil

app = Flask(__name__)
# UPLOAD_FOLDER = 'drive'
UPLOAD_FOLDER = r"C:\Users\KLKA\Videos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return jsonify({'message': 'File uploaded successfully', 'filename': file.filename})

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify({'files': files})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@app.route('/storage-info', methods=['GET'])
def storage_info():
    total, used, free = shutil.disk_usage("drive")  # or just "/"
    return jsonify({
        'total': total,
        'used': used,
        'free': free
    })

if __name__ == '__main__':
    app.run(debug=True)
