import os
from app.models import User
from flask import current_app


def get_folder_size(path):
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_folder_size(entry.path)
    return total


def get_user_upload_folder(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return os.path.join(current_app.config['UPLOAD_FOLDER'], user.folder_name)
    return None


def create_user_folder(folder_path):
    os.makedirs(folder_path, exist_ok=True)
