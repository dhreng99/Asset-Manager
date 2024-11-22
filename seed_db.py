from app import app, db
from models import User, Asset
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        db.create_all()

        # Add default users
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password=generate_password_hash('adminpass', method='pbkdf2:sha256'), role='admin')
            db.session.add(admin)

        if not User.query.filter_by(username='user').first():
            user = User(username='user', password=generate_password_hash('userpass', method='pbkdf2:sha256'), role='user')
            db.session.add(user)

        # Add sample assets
        if not Asset.query.first():  # Check if there are any assets yet
            asset1 = Asset(name='Laptop', description='Dell XPS 13', owner_id=admin.id, created_by='admin')
            asset2 = Asset(name='Monitor', description='ASUS 27-inch', owner_id=admin.id, created_by='admin')
            asset3 = Asset(name='Keyboard', description='Mechanical Keyboard', owner_id=user.id, created_by='user')
            asset4 = Asset(name='Mouse', description='Logitech Wireless', owner_id=user.id, created_by='user')
            db.session.add_all([asset1, asset2, asset3, asset4])

        db.session.commit()
        print("Database seeded successfully.")

if __name__ == "__main__":
    seed_data()