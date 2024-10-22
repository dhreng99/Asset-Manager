from flask import Flask
from models import db, User, Asset

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    # Sample data
    if not User.query.first():
        admin = User(username='admin', password='adminpass', role='admin')
        user1 = User(username='user1', password='userpass', role='user')
        asset1 = Asset(name='Laptop', description='Dell Laptop', owner=admin)

        db.session.add(admin)
        db.session.add(user1)
        db.session.add(asset1)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)