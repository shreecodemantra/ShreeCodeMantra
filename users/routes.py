from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import mongo
from bson import ObjectId

user_bp = Blueprint('users', __name__, url_prefix='/users', static_folder='../static')

@user_bp.route('/aboutus', methods=['GET', 'POST'])
def aboutus():
    return render_template('users/about.html')

@user_bp.route('/services', methods=['GET', 'POST'])
def services():
    try:
        if request.method == 'POST':
            search_query = request.form.get('search', '')
            category_filter = request.form.get('category', '')
        else:
            search_query = ''
            category_filter = ''
        
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
    
@user_bp.route('/project/<project_id>')
def project_details(project_id):
    try:
        project = mongo.db.projects.find_one({'_id': ObjectId(project_id)})
        if not project:
            flash('Project not found', 'error')
            return redirect(url_for('user_bp.services'))

        return render_template('users/project_details.html', project=project)
    except Exception as e:
        flash('Error loading project details', 'error')
        return redirect(url_for('user_bp.services'))

@user_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('users/contact.html')