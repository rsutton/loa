from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user
from flask_login.utils import login_required, logout_user
from floa.models.user import User


bp = Blueprint(
    name='auth',
    import_name=__name__,
    url_prefix="/"
)

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/login_post', methods=['POST'])
def login_post():
    user = User.get(1)
    login_user(user, remember=True)
    return redirect(url_for('home.home'))

@bp.route('/login/callback')
def login_callback():
    return 'Callback'

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.home'))

