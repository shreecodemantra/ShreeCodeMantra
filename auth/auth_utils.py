import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app, render_template

def create_jwt_token(user_id, email):
    """Generate JWT token with expiration"""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def decode_jwt_token(token):
    """Decode and validate JWT token"""
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # You can use either cookie or Authorization header
        token = request.cookies.get('token') or request.headers.get('Authorization')
        if not token:
            return render_template('auth/sign-in.html')

        # If header, strip 'Bearer '
        if isinstance(token, str) and token.startswith("Bearer "):
            token = token.replace("Bearer ", "")

        decoded = decode_jwt_token(token)
        if 'error' in decoded:
            return render_template('auth/sign-in.html')

        # attach decoded user info
        request.user = decoded
        return f(*args, **kwargs)
    return decorated
