from flask import Blueprint, render_template, request, jsonify, make_response, current_app
from werkzeug.security import check_password_hash
from extensions import mongo
from auth.auth_utils import create_jwt_token, token_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login route."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Only find user with role = admin
        admin_user = mongo.db.users.find_one({'email': email, 'role': 'admin'})

        if admin_user and check_password_hash(admin_user['password'], password):
            token = create_jwt_token(admin_user['_id'], email)

            resp = make_response(jsonify({
                "status": "success",
                "message": "Admin login successful!"
            }))
            resp.set_cookie(
                "admin_token",
                token,
                httponly=True,
                secure=False,   # Set True in production (HTTPS)
                samesite="Strict",
                max_age=2 * 60 * 60  # 2 hours
            )
            return resp

        return jsonify({"status": "fail", "error": "Invalid admin credentials!"})

    return render_template('admin/admin-login.html')


@admin_bp.route('/dashboard', methods=['GET'])
@token_required
def dashboard():
    """Admin dashboard - protected route."""
    return render_template('admin/dashboard.html')


@admin_bp.route('/logout', methods=['GET'])
def logout():
    """Admin logout - clear cookie."""
    resp = make_response(jsonify({
        "status": "success",
        "message": "Admin logged out!"
    }))
    resp.delete_cookie("admin_token")
    return resp
