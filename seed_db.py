# seed_db.py
from app import app, db
from models import User, Asset
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # Only seed if tables are successfully created with migrations
        if User.query.count() == 0:
            # Add default users
            admin = User(username='admin', password=generate_password_hash('adminpass', method='pbkdf2:sha256'), role='admin')
            user = User(username='user', password=generate_password_hash('userpass', method='pbkdf2:sha256'), role='user')
            db.session.add_all([admin, user])

            # Add sample assets
            asset1 = Asset(name='Laptop', description='Dell XPS 13', owner_id=1, created_by='admin')
            asset2 = Asset(name='Monitor', description='ASUS 27-inch', owner_id=1, created_by='admin')
            asset3 = Asset(name='Keyboard', description='Mechanical Keyboard', owner_id=2, created_by='user')
            asset4 = Asset(name='Mouse', description='Logitech Wireless', owner_id=2, created_by='user')
            db.session.add_all([asset1, asset2, asset3, asset4])

            db.session.commit()
            print("Database seeded successfully.")

if __name__ == "__main__":
    seed_data()