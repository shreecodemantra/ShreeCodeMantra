from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from extensions import mongo
from bson import ObjectId
from auth.auth_utils import token_required
import math

user_bp = Blueprint('users', __name__, url_prefix='/users', static_folder='../static')

@user_bp.route('/dashboard')
@token_required
def dashboard():
    try:
        user_email = request.user['email']
        user = mongo.db.users.find_one({'email': user_email})
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.sign_in'))
        
        # Query downloaded projects by this user
        downloads = list(mongo.db.downloads.find({'user_id': user['_id']}))
        
        # Extract project details
        downloaded_projects = []
        for dl in downloads:
            proj = mongo.db.projects.find_one({'_id': dl['project_id']})
            if proj:
                proj['download_date'] = dl.get('download_date', '')
                downloaded_projects.append(proj)
                
        return render_template('users/dashboard.html', user=user, downloaded_projects=downloaded_projects)
    except Exception as e:
        flash('Error loading dashboard', 'error')
        return redirect(url_for('.services'))

@user_bp.route('/aboutus', methods=['GET', 'POST'])
def aboutus():
    return render_template('users/about.html')

@user_bp.route('/blogs')
def blogs():
    return render_template("users/blog.html")

@user_bp.route('/services', methods=['GET'])
def services():
    try:
        # -----------------------------------------
        # GET FILTER VALUES
        # -----------------------------------------
        search_query = request.args.get('search', '').strip()
        category_filter = request.args.get('category', '').strip()

        page = request.args.get('page', 1, type=int)
        per_page = 3

        # Prevent invalid page number
        if page < 1:
            page = 1

        # -----------------------------------------
        # BUILD MONGODB QUERY
        # -----------------------------------------
        query = {}

        # Search
        if search_query:
            query['$or'] = [
                {
                    'title': {
                        '$regex': search_query,
                        '$options': 'i'
                    }
                },
                {
                    'description': {
                        '$regex': search_query,
                        '$options': 'i'
                    }
                },
                {
                    'tech_stack': {
                        '$regex': search_query,
                        '$options': 'i'
                    }
                }
            ]

        # Category
        if category_filter:
            query['category'] = category_filter

        # -----------------------------------------
        # TOTAL PROJECTS
        # -----------------------------------------
        total_projects = mongo.db.projects.count_documents(query)

        # -----------------------------------------
        # TOTAL PAGES
        # -----------------------------------------
        if total_projects > 0:
            total_pages = math.ceil(total_projects / per_page)
        else:
            total_pages = 1

        # -----------------------------------------
        # FIX PAGE IF OUT OF RANGE
        # -----------------------------------------
        if page > total_pages:
            page = total_pages

        # -----------------------------------------
        # MONGODB PAGINATION
        # -----------------------------------------
        skip = (page - 1) * per_page

        # -----------------------------------------
        # FETCH PROJECTS
        # -----------------------------------------
        projects = list(
            mongo.db.projects
            .find(query)
            .sort('upload_date', -1)
            .skip(skip)
            .limit(per_page)
        )

        # -----------------------------------------
        # GET CATEGORIES
        # -----------------------------------------
        categories = list(
            mongo.db.categories
            .find()
            .sort('name', 1)
        )

        # -----------------------------------------
        # RENDER PAGE
        # -----------------------------------------
        return render_template(
            'users/services.html',
            projects=projects,
            categories=categories,
            search_query=search_query,
            category_filter=category_filter,
            page=page,
            total_pages=total_pages,
            total_projects=total_projects
        )

    except Exception as e:

        print("SERVICES ERROR:", str(e))

        flash('Error retrieving projects', 'error')

        return render_template(
            'users/services.html',
            projects=[],
            categories=[],
            search_query='',
            category_filter='',
            page=1,
            total_pages=1,
            total_projects=0
        )

        
@user_bp.route('/topics')
def view_topics():
    topics = list(mongo.db.topics.find().sort('created_at', -1))
    return render_template('users/view_topics.html', topics=topics)
    
@user_bp.route('/project/<id_or_slug>')
def project_details(id_or_slug):
    try:
        project = None
        # Try parsing as ObjectId
        if len(id_or_slug) == 24 and all(c in '0123456789abcdefABCDEF' for c in id_or_slug):
            project = mongo.db.projects.find_one({'_id': ObjectId(id_or_slug)})
            if project and project.get('slug'):
                return redirect(url_for('.project_details', id_or_slug=project['slug']), code=301)
        
        # If not found or not an ObjectId, lookup by slug
        if not project:
            project = mongo.db.projects.find_one({'slug': id_or_slug})

        if not project:
            abort(404)

        return render_template('users/project_details.html', project=project)
    except Exception as e:
        flash('Error loading project details', 'error')
        return redirect(url_for('.services'))

@user_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':  
        try:
            fname = request.form['fname']
            email = request.form['email']
            subject = request.form['subject']
            message = request.form['message']

            mongo.db.contact.insert_one({
                'fname': fname,
                'email':email,
                'subject':subject,
                'message':message
            })

            return jsonify({
                "status": "success",
                "message": "Response submitted successfully!"
            })
        except Exception as e:
            return jsonify({"status": "fail", "error": str(e)})
    return render_template('users/contact.html')
