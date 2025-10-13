from flask import Blueprint, render_template, request, make_response, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo
from auth.auth_utils import create_jwt_token, token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user:
            return jsonify({"status": "fail", "error": "User already exists!"})

        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({
            'name': name,
            'email': email,
            'password': hashed_password
        })

        resp = jsonify({
            "status": "success",
            "message": "Registration successful!"
        })
        return resp

    return render_template('auth/sign-up.html')

@auth_bp.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
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

    return render_template('auth/sign-in.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@token_required
def profile():
    if request.method == 'POST':
        return render_template('main/index.html')
    return render_template('main/index.html')
