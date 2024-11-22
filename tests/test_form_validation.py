import pytest
from forms import RegistrationForm, AssetForm
from app import app, db, Asset
from werkzeug.security import generate_password_hash
from wtforms.validators import ValidationError

# Setup and teardown for database state
@pytest.fixture(scope='module', autouse=True)
def setup_database():
    with app.app_context():
        db.create_all()  # Ensure the database and tables are created before tests
        yield  # Run tests
        db.drop_all()  # Clean-up after tests

# Helper function to provide app context for form validation
def validate_registration_form(username, password, confirm_password):
    with app.app_context():
        form = RegistrationForm(data={'username': username, 'password': password, 'confirm_password': confirm_password})
        form.validate()
        return form

def test_password_complexity():
    username = "testuser"
    simple_password = "password"
    complex_password = "Passw0rd$"

    with app.app_context():  # Use context for potential dependencies
        form = RegistrationForm(data={'username': username, 'password': simple_password, 'confirm_password': simple_password})
        assert not form.validate()  # Expect this to return False

        form = RegistrationForm(data={'username': username, 'password': complex_password, 'confirm_password': complex_password})
        assert form.validate()  # Expect this to pass

# Test username length rules
def test_username_length():
    short_username = "ab"
    valid_username = "validuser"

    with app.app_context():
        form = RegistrationForm(data={'username': short_username, 'password': "Passw0rd!", 'confirm_password': "Passw0rd!"})
        assert not form.validate()  # Expect this to fail

        form = RegistrationForm(data={'username': valid_username, 'password': "Passw0rd!", 'confirm_password': "Passw0rd!"})
        assert form.validate()  # Expect this to pass

# Fixture for setting up a test asset in the database
@pytest.fixture
def test_asset():
    with app.app_context():
        asset = Asset(name='Test Asset', description='Description', owner_id=1)
        db.session.add(asset)
        db.session.commit()
        yield asset  # Provide asset for the test
        db.session.delete(asset)  # Clean up
        db.session.commit()

# Test asset name uniqueness
def test_asset_name_uniqueness(test_asset):
    with app.app_context():
        form = AssetForm(data={'name': 'Test Asset', 'description': 'Another Description'})
        assert not form.validate()  # Expect this to fail due to duplicate name
        assert 'exists' in form.name.errors[0]  # Verify specific error message content