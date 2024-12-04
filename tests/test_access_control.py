import pytest
from app import app as flask_app, db
from app import User, Asset
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    # Configures the Flask application for testing, using an in-memory SQLite database
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with flask_app.test_client() as client:
        with flask_app.app_context():
            # Create all database tables
            db.create_all()

            # Clear any existing data
            db.session.query(User).delete()
            db.session.query(Asset).delete()
            db.session.commit()

            # Add test users: an admin and a regular user
            admin = User(username='admin', password=generate_password_hash('adminpass', method='pbkdf2:sha256'), role='admin')
            regular_user = User(username='user', password=generate_password_hash('user123', method='pbkdf2:sha256'), role='user')

            db.session.add(admin)
            db.session.add(regular_user)
            db.session.commit()

            yield client

        with flask_app.app_context():
            # Clean up database tables after tests
            db.drop_all()

# Helper function to log in a user by sending POST request to the login endpoint
def login(client, username, password):
    response = client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)
    if b'Logged in successfully.' not in response.data:
        print(response.data)
        raise AssertionError('Login failed')
    return response

# Test to verify that an admin user can delete an asset
def test_admin_access(client):
    login(client, 'admin', 'adminpass')

    with flask_app.app_context():
        # Create a test asset owned by the admin
        admin = User.query.filter_by(username='admin').first()
        asset = Asset(name='AdminTestAsset', description='An asset by admin', owner_id=admin.id)
        db.session.add(asset)
        db.session.commit()

        asset_id = asset.id
        
    # Admin attempts to delete the asset
    response = client.post(f'/assets/delete/{asset_id}', follow_redirects=True)
    # Check that the asset deletion succeeded
    assert b'Asset deleted successfully.' in response.data

# Test to check that a regular user cannot delete assets
def test_regular_user_no_delete_access(client):
    login(client, 'user', 'user123')

    with flask_app.app_context():
        # Create a test asset owned by the regular user
        user = User.query.filter_by(username='user').first()
        asset = Asset(name='UserAsset', description='An asset for testing', owner_id=user.id)
        db.session.add(asset)
        db.session.commit()

        asset_id = asset.id

    # Regular user attempts to delete an asset, which should be forbidden
    response = client.post(f'/assets/delete/{asset_id}')
    assert response.status_code == 403
    assert b'Forbidden' in response.data  # Validate that the forbidden content was served