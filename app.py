from flask import Flask, request, jsonify
from flask_cors import CORS
from extensions import db
from models import User
from flask_migrate import Migrate
import bcrypt
import os

app = Flask(__name__)
CORS(app)

# Set your DATABASE URL in environment variables or hardcode here (not recommended)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://myapp_db_kcws_user:g1y5Cbar0Hez50awL6G723G5pFdVkZUk@dpg-d0s3ig24d50c73b825m0-a.oregon-postgres.render.com/myapp_db_kcws'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    phone = data.get('phone')
    email = data.get('email')
    password = data.get('password')

    if not all([username, phone, email, password]):
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'User already exists'}), 409

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(username=username, phone=phone, email=email, password_hash=hashed_password.decode('utf-8'))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'message': 'Login successful', 'username': user.username}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.with_entities(User.id, User.username, User.phone, User.email).all()
    users_list = [dict(id=u.id, username=u.username, phone=u.phone, email=u.email) for u in users]
    return jsonify(users_list)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
