from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta
from models import db, Admin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['OPTIONS', 'POST'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({"message": "CORS preflight successful"}), 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if Admin.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_admin = Admin(username=username, password=hashed_password)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'message': 'Admin registered successfully'}), 201

@auth_bp.route('/login', methods=['OPTIONS', 'POST'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({"message": "CORS preflight successful"}), 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    admin = Admin.query.filter_by(username=username).first()
    if not admin or not check_password_hash(admin.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # ✅ Issue access token valid for 7 days
    access_token = create_access_token(identity=username, expires_delta=timedelta(days=7))

    return jsonify({'access_token': access_token}), 200
