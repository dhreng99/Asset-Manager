import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        with app.app_context():
            # Create a test user in the db
            db.create_all()
            user = User(username='testuser', password=generate_password_hash('testpass', method='pbkdf2:sha256'), role='user')
            db.session.add(user)
            db.session.commit()
            yield client
            db.drop_all()

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_xss_sanitization(client):
    # Log in the test client
    login(client, 'testuser', 'testpass')

    # Attempt to inject a script via description
    xss_script = "<script>alert('XSS');</script>"
    response = client.post('/assets/new', data={
        'name': 'Asset With XSS',
        'description': xss_script
    }, follow_redirects=True)

    # Inspect the actual response to find the correct escape sequence (adjust as needed)
    print(response.data)  # Debugging: View the precise output

    # Check if the response includes the expected escaped content
    assert b"&lt;script&gt;alert(&#39;XSS&#39;);&lt;/script&gt;" in response.data or b"&lt;script&gt;alert('XSS');&lt;/script&gt;" in response.data
    assert response.status_code == 200

def test_password_hashing():
    password = "SecurePass123!"
    hashed_password = generate_password_hash(password)

    # Ensure the original password matches the hashed version
    assert check_password_hash(hashed_password, password)

    # Ensure a different password does not match the hashed version
    assert not check_password_hash(hashed_password, "WrongPassword")