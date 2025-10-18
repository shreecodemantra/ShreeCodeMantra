from flask import Blueprint, render_template, request, make_response, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo, mail
from auth.auth_utils import create_jwt_token, token_required
import random
from flask_mail import Message

user_bp = Blueprint('users', __name__, url_prefix='/users')

@user_bp.route('/aboutus', methods=['GET', 'POST'])
def aboutus():
    return render_template('users/about.html')

@user_bp.route('/services', methods=['GET', 'POST'])
def services():
    return render_template('users/services.html')

@user_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('users/contact.html')
