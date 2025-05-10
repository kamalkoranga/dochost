from flask import render_template, redirect, url_for, request, current_app
from flask_login import login_user, logout_user, current_user
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.models import User
from app.utils import create_user_folder
import os


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user: User = db.session.scalar(
            sa.select(User).where(User.username == username)
        )

        if user is None or not user.check_password(password):
            return render_template('login.html', error="Invalid username or password")

        login_user(user, remember=True)
        return redirect(url_for('main.index'))

    return render_template('login.html')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user: User = User.query.filter_by(username=username).first()
        if user:
            return render_template('register.html', error="Username already exists")

  
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_user.folder_name)
        create_user_folder(folder_path)
        return redirect(url_for('auth.login'))

    return render_template('register.html')
