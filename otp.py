import random
import requests
from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from models import db


# Blueprint for OTP routes
otp_bp = Blueprint('otp', __name__)

# SMS Gateway Configuration
SMS_GATEWAY_API_KEY = 'your_api_key'  # Replace with your SMS Gateway API key
SMS_GATEWAY_DEVICE_ID = 'your_device_id'  # Replace with your SMS Gateway device ID
SMS_GATEWAY_URL = 'https://smsgateway.me/api/v4/message/send'

# OTP model
class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(15), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper function to send SMS via SMS Gateway
def send_sms_via_gateway(phone_number, message):
    payload = [
        {
            "phone_number": phone_number,
            "message": message,
            "device_id": SMS_GATEWAY_DEVICE_ID
        }
    ]
    headers = {'Authorization': SMS_GATEWAY_API_KEY}
    response = requests.post(SMS_GATEWAY_URL, json=payload, headers=headers)
    return response

@otp_bp.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.json
    number = data.get('number')

    if not number:
        return jsonify({'message': 'Mobile number is required.'}), 400

    otp_code = f"{random.randint(100000, 999999)}"

    existing_otp = OTP.query.filter_by(number=number).first()
    if existing_otp:
        db.session.delete(existing_otp)

    new_otp = OTP(number=number, otp=otp_code)
    db.session.add(new_otp)
    db.session.commit()

    try:
        # Send OTP via SMS Gateway
        response = send_sms_via_gateway(number, f"Your OTP code is {otp_code}")
        if response.status_code != 200:
            raise Exception(response.text)
    except Exception as e:
        return jsonify({'message': f"Failed to send OTP: {str(e)}"}), 500

    return jsonify({'message': 'OTP sent successfully.'}), 200

@otp_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.json
    number = data.get('number')
    otp = data.get('otp')

    if not number or not otp:
        return jsonify({'message': 'Mobile number and OTP are required.'}), 400

    record = OTP.query.filter_by(number=number).first()

    if not record:
        return jsonify({'message': 'Invalid OTP or number.'}), 400

    # Check OTP validity (5 minutes expiration)
    if datetime.utcnow() > record.created_at + timedelta(minutes=5):
        db.session.delete(record)
        db.session.commit()
        return jsonify({'message': 'OTP expired. Please request a new one.'}), 400

    if record.otp != otp:
        return jsonify({'message': 'Invalid OTP.'}), 400

    db.session.delete(record)
    db.session.commit()

    return jsonify({'message': 'OTP verified successfully.'}), 200
