from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Asset
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from forms import RegistrationForm, LoginForm, AssetForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_key')  
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///assets.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True  # Use HTTPS to securely transmit cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Enforce SameSite policy to protect against CSRF

db.init_app(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        flash('Registration successful.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/assets/new', methods=['GET', 'POST'])
@login_required
def new_asset():
    form = AssetForm()
    if form.validate_on_submit():
        # Check for existing asset name
        existing_asset = Asset.query.filter_by(name=form.name.data).first()
        if existing_asset:
            flash('An asset with this name already exists. Please choose a different name.', 'warning')
            return render_template('new_asset.html', form=form)

        asset = Asset(name=form.name.data, description=form.description.data, owner_id=current_user.id, created_by=current_user.username)
        db.session.add(asset)
        db.session.commit()
        flash('Asset created successfully.', 'success')
        return redirect(url_for('list_assets'))
    return render_template('new_asset.html', form=form)

@app.route('/assets')
@login_required
def list_assets():
    assets = Asset.query.all()
    return render_template('list_assets.html', assets=assets)

@app.route('/assets/edit/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    form = AssetForm(obj=asset)  # Pre-populate form with existing asset data
    if form.validate_on_submit():
        asset.name = form.name.data
        asset.description = form.description.data
        db.session.commit()
        flash('Asset updated successfully.', 'success')
        return redirect(url_for('list_assets'))
    return render_template('edit_asset.html', form=form)

@app.route('/assets/delete/<int:asset_id>', methods=['POST'])
@admin_required
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted successfully.', 'success')
    return redirect(url_for('list_assets'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Sample data seeding
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password=generate_password_hash('adminpass', method='pbkdf2:sha256'), role='admin')
            db.session.add(admin)

        if not User.query.filter_by(username='user').first():
            user = User(username='user', password=generate_password_hash('userpass', method='pbkdf2:sha256'), role='user')
            db.session.add(user)

        db.session.commit()

    app.run(debug=True)