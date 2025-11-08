from flask import Blueprint, render_template, request, make_response, jsonify, redirect, g
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo, mail
from auth.auth_utils import create_jwt_token, token_required, decode_jwt_token
import random
from flask_mail import Message
import time

otp_store = {}

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.before_app_request
def load_logged_in_user():
    token = request.cookies.get('token')
    g.user = None

    if token:
        decoded = decode_jwt_token(token)
        if 'error' not in decoded:
            user = mongo.db.users.find_one({'email': decoded['email']})
            if user:
                g.user = {
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "_id": str(user.get("_id"))
                }

@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        try:
            email = request.form['email']

            existing_user = mongo.db.users.find_one({'email': email})
            if existing_user:
                return jsonify({"status": "fail", "error": "User already exists!"})

            otp = str(random.randint(100000, 999999))

            expiry = time.time() + 300  # 5 minutes validity

            otp_store[email] = {"otp": otp, "expiry": expiry}

            # send OTP email
            msg = Message("Your Shree Code Mantra OTP",
                        recipients=[email],
                        body=f"Your OTP for registration is {otp}")
            mail.send(msg)

            return jsonify({
                "status": "otp_sent",
                "message": f"OTP sent to {email}. Please enter it below."
            })
        except Exception as e:
            return jsonify({"status": "fail", "error": str(e)})
    return render_template('auth/sign-up.html')

@auth_bp.route('/otpvalidate', methods=['POST'])
def validate_otp():
    try:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        otp = request.form['otpInput']

        if email not in otp_store:
            return jsonify({"status": "fail", "error": "No OTP found or expired."})

        record = otp_store[email]

        if time.time() > record['expiry']:
            otp_store.pop(email, None)
            return jsonify({"status": "fail", "error": "OTP expired. Please request again."})

        if otp != record['otp']:
            return jsonify({"status": "fail", "error": "Invalid OTP."})

        mongo.db.users.insert_one({
            'name': name,
            'email':email,
            'password':generate_password_hash(password)
        })

        return jsonify({
            "status": "success",
            "message": "Registration successful!"
        })
    except Exception as e:
        return jsonify({"status": "fail", "error": str(e)})

@auth_bp.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']

            user = mongo.db.users.find_one({'email': email})
            if user and check_password_hash(user['password'], password):
                token = create_jwt_token(user['_id'], email)

                resp = make_response(jsonify({
                    "status": "success",
                    "message": "Login successful!"
                }))
                resp.set_cookie(
                    "token",
                    token,
                    httponly=True,
                    secure=False,    # True in production
                    samesite="Strict",
                    max_age=2 * 60 * 60
                )
                return resp

            return jsonify({"status": "fail", "error": "Invalid credentials!"})
        except Exception as e:
            return jsonify({"status": "fail", "error": str(e)})
    return render_template('auth/sign-in.html')

@auth_bp.route('/logout')
def logout():
    response = redirect('/')
    response.delete_cookie('token')
    return response