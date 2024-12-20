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

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
# Set secret key for secure sessions
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_key')  
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///assets.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True  # Use HTTPS to securely transmit cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Enforce SameSite policy to protect against CSRF

# Initialize the database with the Flask app and enable migrations
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
# Function to load a user from the database by user ID
def load_user(user_id):
    return db.session.get(User, int(user_id))

def admin_required(f):
    # Decorator to require admin role for accessing certain views
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            # Aborts with 403 Forbidden if the user is not an admin
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
# Home route showing the number of assets and the most recent asset
def home():
    total_assets = Asset.query.count()
    recent_asset = Asset.query.order_by(Asset.date_created.desc()).first()
    return render_template('index.html', total_assets=total_assets, recent_asset=recent_asset)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login route for user authentication
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
# Route to log out the user
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
# Route for user registration
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
# Route for creating a new asset
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
# Route that lists all assets
def list_assets():
    assets = Asset.query.all()
    return render_template('list_assets.html', assets=assets)

@app.route('/assets/edit/<int:asset_id>', methods=['GET', 'POST'])
@login_required
# Route to edit an asset based on its id
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    form = AssetForm(obj=asset, original_name=asset.name)  # Pass original_name to the form
    if form.validate_on_submit():
        asset.name = form.name.data
        asset.description = form.description.data
        db.session.commit()
        flash('Asset updated successfully.', 'success')
        return redirect(url_for('list_assets'))
    return render_template('edit_asset.html', form=form)

@app.route('/assets/delete/<int:asset_id>', methods=['POST'])
@admin_required
# Route to delete an asset; admin access required
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted successfully.', 'success')
    return redirect(url_for('list_assets'))

if __name__ == "__main__":
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        # Sample data seeding
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password=generate_password_hash('adminpass', method='pbkdf2:sha256'), role='admin')
            db.session.add(admin)

        if not User.query.filter_by(username='user').first():
            user = User(username='user', password=generate_password_hash('userpass', method='pbkdf2:sha256'), role='user')
            db.session.add(user)

        db.session.commit()
    # Start the Flask app
    app.run(debug=True)