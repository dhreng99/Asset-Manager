# tests/test_assets.py
import pytest
from app import app as flask_app, db
from app import User, Asset
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing ease
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with flask_app.test_client() as client:
        with flask_app.app_context():
            db.create_all()
            yield client
        with flask_app.app_context():
            db.drop_all()

@pytest.fixture
def app():
    return flask_app

def login(client, username, password):
    response = client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)
    assert b'Logged in successfully.' in response.data
    return response

def test_create_asset(client, app):
    with app.app_context():
        user = User(username='testuser', password=generate_password_hash('testpass', method='pbkdf2:sha256'), role='user')
        db.session.add(user)
        db.session.commit()

    login(client, 'testuser', 'testpass')

    response = client.post('/assets/new', data={
        'name': 'New Asset', 
        'description': 'Asset description'
    }, follow_redirects=True)

    assert b'Asset created successfully.' in response.data
    assert b'New Asset' in response.data
    with app.app_context():
        assert Asset.query.filter_by(name='New Asset').first() is not None

def test_list_assets(client, app):
    with app.app_context():
        user = User(username='testuser', password=generate_password_hash('testpass', method='pbkdf2:sha256'), role='user')
        db.session.add(user)
        db.session.commit()
        asset = Asset(name='Test Asset', description='Test description', owner_id=user.id)
        db.session.add(asset)
        db.session.commit()

    login(client, 'testuser', 'testpass')

    response = client.get('/assets')
    assert response.status_code == 200
    assert b'Test Asset' in response.data