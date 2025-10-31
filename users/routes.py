from flask import Blueprint, render_template, request, make_response, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo, mail
from auth.auth_utils import create_jwt_token, token_required
import random
from flask_mail import Message

user_bp = Blueprint('users', __name__, url_prefix='/users', static_folder='../static')

@user_bp.route('/aboutus', methods=['GET', 'POST'])
def aboutus():
    return render_template('users/about.html')

@user_bp.route('/services', methods=['GET', 'POST'])
def services():
    try:
        search_query = request.args.get('search', '')
        category_filter = request.args.get('category', '')
        
        query = {}
        
        if search_query:
            query['$or'] = [
                {'title': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}},
                {'tech_stack': {'$in': [search_query]}}
            ]
        
        if category_filter:
            query['category'] = category_filter
        
        projects = list(mongo.db.projects.find(query).sort('upload_date', -1))
        categories = list(mongo.db.categories.find())
        
        return render_template('users/services.html', 
                             projects=projects, 
                             categories=categories,
                             search_query=search_query,
                             category_filter=category_filter)
    except Exception as e:
        flash('Error retrieving projects', 'error')
        return render_template('users/services.html', projects=[])

@user_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('users/contact.html')