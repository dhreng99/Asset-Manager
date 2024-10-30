# app.py

from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Asset
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'warning')
        else:
            password_hashed = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=password_hashed, role='user')
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/assets/new', methods=['GET', 'POST'])
@login_required
def new_asset():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_asset = Asset(name=name, description=description, owner_id=current_user.id)
        db.session.add(new_asset)
        db.session.commit()
        flash('Asset created successfully.', 'success')
        return redirect(url_for('list_assets'))
    return render_template('new_asset.html')

@app.route('/assets')
@login_required
def list_assets():
    assets = Asset.query.all()
    return render_template('list_assets.html', assets=assets)

@app.route('/assets/edit/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    if request.method == 'POST':
        asset.name = request.form['name']
        asset.description = request.form['description']
        db.session.commit()
        flash('Asset updated successfully.', 'success')
        return redirect(url_for('list_assets'))
    return render_template('edit_asset.html', asset=asset)

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