from flask import Blueprint, request, jsonify
from models import db, User, Address
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        number = data.get('number')
        password = data.get('password')
        name = data.get('name', 'User')

        if not number or not password:
            return jsonify({'message': 'Number and password are required.'}), 400

        ext_user = User.query.filter_by(number=number).first()
        if ext_user:
            return jsonify({'message': 'User with this number already exists.'}), 400

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(number=number, password=hashed_password, name=name)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully.', 'user_id': new_user.id}), 201

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'message': 'An error occurred during registration.', 'error': str(e)}), 500

@user_bp.route('/chk/<string:num>', methods=['GET'])
def chk(num):
    try:
        if not num:
            return jsonify({'message': 'Number is required.'}), 400

        user = User.query.filter_by(number=num).first()
        if user:
            return jsonify({'message': 'Old User', 'IsNew': 'False'}), 200
        else:
            return jsonify({'message': 'New User', 'IsNew': 'True'}), 200

    except Exception as e:
        return jsonify({'message': 'An error occurred while checking user.', 'error': str(e)}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        number = data.get('number')
        password = data.get('password')

        if not number or not password:
            return jsonify({'message': 'Number and password are required.'}), 400

        user = User.query.filter_by(number=number).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid number or password.'}), 401

        return jsonify({'message': 'Login successful.', 'user_id': user.id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred during login.', 'error': str(e)}), 500

@user_bp.route('/add_address', methods=['POST'])
def add_address():
    try:
        data = request.json
        user_id = data.get('user_id')
        street = data.get('street')
        city = data.get('city')
        state = data.get('state')
        zip_code = data.get('zip_code')

        if not user_id or not street or not city or not state or not zip_code:
            return jsonify({'message': 'All fields are required.'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        new_address = Address(user_id=user_id, street=street, city=city, state=state, zip_code=zip_code)
        db.session.add(new_address)
        db.session.commit()

        return jsonify({'message': 'Address added successfully.'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while adding address.', 'error': str(e)}), 500