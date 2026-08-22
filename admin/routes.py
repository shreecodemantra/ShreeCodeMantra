from bson import ObjectId
from flask import Blueprint, flash, redirect, render_template, request, jsonify, make_response, current_app, send_file, send_from_directory, url_for
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from extensions import mongo
from auth.auth_utils import admin_token_required, create_jwt_token, token_required
import os
from datetime import datetime
from utils.slug import slugify
import math

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# File upload configuration
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', '7z'}
ALLOWED_EXTENSIONS1 = {'pdf', 'doc', 'docx'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file1(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS1


def save_file(file, subfolder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', UPLOAD_FOLDER), subfolder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Add timestamp to avoid filename conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(upload_path, filename)
        file.save(filepath)
        return filepath.replace('static/', '')
    return None


def save_file1(file, subfolder):
    if file and allowed_file1(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', UPLOAD_FOLDER), subfolder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Add timestamp to avoid filename conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(upload_path, filename)
        file.save(filepath)
        return filepath.replace('static/', '')
    return None

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login route."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Only find user with role = admin
        admin_user = mongo.db.admin.find_one({'email': email, 'role': 'admin'})

        if admin_user and check_password_hash(admin_user['password'], password):
            token = create_jwt_token(str(admin_user['_id']), email)

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
                max_age=2 * 60 * 60,  # 2 hours
                path='/'
            )
            return resp

        return jsonify({"status": "fail", "error": "Invalid admin credentials!"})

    return render_template('admin/admin-login.html')

@admin_bp.route('/dashboard', methods=['GET'])
@admin_token_required
def dashboard():
    """Admin dashboard - protected route."""
    # Get stats for dashboard
    total_projects = mongo.db.projects.count_documents({})
    total_categories = mongo.db.categories.count_documents({})
    
    # Get recent projects
    recent_projects = list(mongo.db.projects.find().sort('upload_date', -1).limit(5))
    
    return render_template('admin/dashboard.html', 
                         total_projects=total_projects,
                         total_categories=total_categories,
                         recent_projects=recent_projects)

@admin_bp.route('/logout', methods=['POST'])
def logout():
    """Admin logout - clear cookie."""
    resp = make_response(jsonify({
        "status": "success",
        "message": "Admin logged out!"
    }))
    resp.delete_cookie("admin_token", path='/')
    return resp

@admin_bp.route('/add_projects', methods=['GET'])
@admin_token_required
def add_projects():
    """Admin add_projects - protected route."""
    categories = list(mongo.db.categories.find())
    return render_template('admin/add_projects.html', categories=categories)

@admin_bp.route('/add_project', methods=['POST'])
@admin_token_required
def add_project():
    try:
        # Get form data
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        tech_stack = [tech.strip() for tech in request.form.get('tech_stack', '').split(',')]
        price = float(request.form.get('price', 0))
        
        # Handle file uploads
        files = {}
        
        # Main image
        main_image = request.files.get('main_image')
        if main_image and main_image.filename:
            main_image_path = save_file(main_image, 'main_images')
            if main_image_path:
                files['main_image'] = main_image_path
        
        # Additional images
        additional_images = request.files.getlist('images')
        image_paths = []
        for image in additional_images:
            if image and image.filename:
                image_path = save_file(image, 'additional_images')
                if image_path:
                    image_paths.append(image_path)
        if image_paths:
            files['images'] = image_paths
        
        # Report
        report = request.files.get('report')
        if report and report.filename:
            report_path = save_file(report, 'reports')
            if report_path:
                files['report'] = report_path
        
        # Code
        code = request.files.get('code')
        if code and code.filename:
            code_path = save_file(code, 'code')
            if code_path:
                files['code'] = code_path
        
        # Demo video URL
        demo_video = request.form.get('demo_video')
        if demo_video:
            files['demo_video'] = demo_video
        
        # Create project document
        project = {
            "title": title,
            "slug": slugify(title),
            "category": category,
            "description": description,
            "tech_stack": tech_stack,
            "price": price,
            "upload_date": datetime.now().strftime("%Y-%m-%d"),
            "files": files
        }
        
        # Insert into MongoDB
        result = mongo.db.projects.insert_one(project)
        
        return jsonify({
            "success": True,
            "message": "Project added successfully",
            "project_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error adding project: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error adding project: {str(e)}"
        }), 500

@admin_bp.route('/add_category', methods=['POST'])
@admin_token_required
def add_category():
    try:
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Check if category already exists
        existing_category = mongo.db.categories.find_one({"name": name})
        if existing_category:
            return jsonify({
                "success": False,
                "message": "Category already exists"
            }), 400
        
        # Create category document
        category = {
            "name": name,
            "description": description
        }
        
        # Insert into MongoDB
        result = mongo.db.categories.insert_one(category)
        
        return jsonify({
            "success": True,
            "message": "Category added successfully",
            "category_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error adding category: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error adding category: {str(e)}"
        }), 500

@admin_bp.route('/get_categories')
@admin_token_required
def get_categories():
    categories = list(mongo.db.categories.find({}, {'_id': 0, 'name': 1}))
    return jsonify(categories)

@admin_bp.route('/categories')
@admin_token_required
def view_categories():
    """View all categories."""
    try:
        categories = list(mongo.db.categories.find().sort('name', 1))
        return render_template('admin/categories.html', categories=categories)
    except Exception as e:
        current_app.logger.error(f"Error retrieving categories: {str(e)}")
        flash('Error retrieving categories', 'error')
        return render_template('admin/categories.html', categories=[])

def get_project_by_id_or_slug(id_or_slug):
    """Helper to fetch a project by ObjectId or slug."""
    project = None
    if len(id_or_slug) == 24 and all(c in '0123456789abcdefABCDEF' for c in id_or_slug):
        project = mongo.db.projects.find_one({'_id': ObjectId(id_or_slug)})
    if not project:
        project = mongo.db.projects.find_one({'slug': id_or_slug})
    return project

@admin_bp.route('/projects')
@admin_token_required
def view_projects():
    """View all projects with search and filter functionality."""
    try:
        search_query = request.args.get('search', '')
        category_filter = request.args.get('category', '')
        page = request.args.get('page', 1, type=int)
        per_page = 9
        
        query = {}
        
        if search_query:
            query['$or'] = [
                {'title': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}},
                {'tech_stack': {'$in': [search_query]}}
            ]
        
        if category_filter:
            query['category'] = category_filter
            
        total_projects = mongo.db.projects.count_documents(query)
        total_pages = math.ceil(total_projects / per_page)
        
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
            
        skip = (page - 1) * per_page
        
        projects = list(mongo.db.projects.find(query).sort('upload_date', -1).skip(skip).limit(per_page))
        categories = list(mongo.db.categories.find())
        
        return render_template('admin/projects.html', 
                             projects=projects, 
                             categories=categories,
                             search_query=search_query,
                             category_filter=category_filter,
                             page=page,
                             total_pages=total_pages)
    except Exception as e:
        current_app.logger.error(f"Error retrieving projects: {str(e)}")
        flash('Error retrieving projects', 'error')
        return render_template('admin/projects.html', projects=[], page=1, total_pages=1)
    
@admin_bp.route('/project/<id_or_slug>')
@admin_token_required
def view_project(id_or_slug):
    """View single project details."""
    try:
        project = get_project_by_id_or_slug(id_or_slug)
        if not project:
            flash('Project not found', 'error')
            return redirect(url_for('admin.view_projects'))
        
        return render_template('admin/project_detail.html', project=project)
    except Exception as e:
        current_app.logger.error(f"Error retrieving project: {str(e)}")
        flash('Error retrieving project', 'error')
        return redirect(url_for('admin.view_projects'))

@admin_bp.route('/project/edit/<id_or_slug>', methods=['GET'])
@admin_token_required
def edit_project_form(id_or_slug):
    """Show edit project form."""
    try:
        project = get_project_by_id_or_slug(id_or_slug)
        categories = list(mongo.db.categories.find())
        
        if not project:
            flash('Project not found', 'error')
            return redirect(url_for('admin.view_projects'))
        
        return render_template('admin/edit_project.html', 
                             project=project, 
                             categories=categories)
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error loading project for editing: {str(e)}")
        flash(f'Error loading project: {str(e)}', 'error')
        return redirect(url_for('admin.view_projects'))

@admin_bp.route('/project/edit/<id_or_slug>', methods=['POST'])
@admin_token_required
def update_project(id_or_slug):
    """Update project data."""
    try:
        # Get form data
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        tech_stack = [tech.strip() for tech in request.form.get('tech_stack', '').split(',')]
        price = float(request.form.get('price', 0))
        
        # Get existing project data
        existing_project = get_project_by_id_or_slug(id_or_slug)
        if not existing_project:
            return jsonify({
                "success": False,
                "message": "Project not found"
            }), 404
        
        # Start with existing files
        files = existing_project.get('files', {})
        
        # Handle new file uploads
        # Main image
        main_image = request.files.get('main_image')
        if main_image and main_image.filename:
            main_image_path = save_file(main_image, 'main_images')
            if main_image_path:
                files['main_image'] = main_image_path
        
        # Additional images
        additional_images = request.files.getlist('images')
        new_image_paths = []
        for image in additional_images:
            if image and image.filename:
                image_path = save_file(image, 'additional_images')
                if image_path:
                    new_image_paths.append(image_path)
        if new_image_paths:
            # Keep existing images and add new ones
            existing_images = files.get('images', [])
            files['images'] = existing_images + new_image_paths
        
        # Report
        report = request.files.get('report')
        if report and report.filename:
            report_path = save_file(report, 'reports')
            if report_path:
                files['report'] = report_path
        
        # Code
        code = request.files.get('code')
        if code and code.filename:
            code_path = save_file(code, 'code')
            if code_path:
                files['code'] = code_path
        
        # Demo video URL
        demo_video = request.form.get('demo_video')
        if demo_video:
            files['demo_video'] = demo_video
        
        # Update project document
        update_data = {
            "title": title,
            "slug": slugify(title),
            "category": category,
            "description": description,
            "tech_stack": tech_stack,
            "price": price,
            "updated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "files": files
        }
        
        # Update in MongoDB
        result = mongo.db.projects.update_one(
            {'_id': existing_project['_id']},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({
                "success": True,
                "message": "Project updated successfully"
            }), 200
        else:
            return jsonify({
                "success": True,
                "message": "No changes made to the project"
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"Error updating project: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error updating project: {str(e)}"
        }), 500

@admin_bp.route('/project/delete/<id_or_slug>', methods=['DELETE'])
@admin_token_required
def delete_project(id_or_slug):
    """Delete project and related downloads."""
    try:
        project = get_project_by_id_or_slug(id_or_slug)
        if not project:
            return jsonify({
                "success": False,
                "message": "Project not found"
            }), 404
            
        # Delete project
        result = mongo.db.projects.delete_one({'_id': project['_id']})
        
        if result.deleted_count > 0:
            # Delete related downloads
            mongo.db.downloads.delete_many({'project_id': project['_id']})
            
            return jsonify({
                "success": True,
                "message": "Project deleted successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Project not found"
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error deleting project: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error deleting project: {str(e)}"
        }), 500

@admin_bp.route('/api/project/<id_or_slug>')
@admin_token_required
def get_project_details(id_or_slug):
    """API endpoint to get project details for modal view."""
    try:
        project = get_project_by_id_or_slug(id_or_slug)
        if project:
            # Convert ObjectId to string for JSON serialization
            project['_id'] = str(project['_id'])
            # Ensure all fields are present
            if 'files' not in project:
                project['files'] = {}
            if 'tech_stack' not in project:
                project['tech_stack'] = []
            if 'price' not in project:
                project['price'] = 0
            if 'upload_date' not in project:
                project['upload_date'] = 'Unknown'
                
            return jsonify({
                "success": True,
                "project": project
            })
        else:
            return jsonify({
                "success": False,
                "message": "Project not found"
            }), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving project: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving project: {str(e)}"
        }), 500

@admin_bp.route('/category/delete/<category_id>', methods=['DELETE'])
@admin_token_required
def delete_category(category_id):
    """Delete category if no projects are using it."""
    try:
        # Check if category exists
        category = mongo.db.categories.find_one({'_id': ObjectId(category_id)})
        if not category:
            return jsonify({
                "success": False,
                "message": "Category not found"
            }), 404
        
        # Check if any projects are using this category
        projects_count = mongo.db.projects.count_documents({'category': category['name']})
        
        if projects_count > 0:
            return jsonify({
                "success": False,
                "message": f"Cannot delete category. {projects_count} project(s) are using it."
            }), 400
        
        # Delete category
        result = mongo.db.categories.delete_one({'_id': ObjectId(category_id)})
        
        if result.deleted_count > 0:
            return jsonify({
                "success": True,
                "message": "Category deleted successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to delete category"
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error deleting category: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error deleting category: {str(e)}"
        }), 500

@admin_bp.route('/downloads')
@admin_token_required
def view_downloads():
    """View download statistics."""
    try:
        # Get downloads with project and user details
        pipeline = [
            {
                '$lookup': {
                    'from': 'projects',
                    'localField': 'project_id',
                    'foreignField': '_id',
                    'as': 'project'
                }
            },
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user'
                }
            },
            {
                '$unwind': '$project'
            },
            {
                '$unwind': {
                    'path': '$user',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$sort': {'download_date': -1}
            },
            {
                '$limit': 100
            }
        ]
        
        downloads = list(mongo.db.downloads.aggregate(pipeline))
        return render_template('admin/downloads.html', downloads=downloads)
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving downloads: {str(e)}")
        flash('Error retrieving download statistics', 'error')
        return render_template('admin/downloads.html', downloads=[])

@admin_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)


@admin_bp.route('/edit_category/<category_id>', methods=['PUT'])
@admin_token_required
def edit_category(category_id):
    try:
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Check if category exists
        existing_category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
        if not existing_category:
            return jsonify({
                "success": False,
                "message": "Category not found"
            }), 404
        
        # Check if new name conflicts with other categories
        conflicting_category = mongo.db.categories.find_one({
            "name": name,
            "_id": {"$ne": ObjectId(category_id)}
        })
        if conflicting_category:
            return jsonify({
                "success": False,
                "message": "Category name already exists"
            }), 400
        
        # Update category
        update_data = {
            "name": name,
            "description": description,
            "updated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        result = mongo.db.categories.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({
                "success": True,
                "message": "Category updated successfully"
            }), 200
        else:
            return jsonify({
                "success": True,
                "message": "No changes made to the category"
            }), 200
            
    except Exception as e:
        current_app.logger.error(f"Error updating category: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error updating category: {str(e)}"
        }), 500

############################################################# Topic Route #############################################################


@admin_bp.route('/topics', methods=['GET'])
@admin_token_required
def topics():
    try:
        topics_list = list(mongo.db.topics.find().sort("created_at", -1))
        categories = list(mongo.db.categories.find())
        return render_template('admin/topics.html', topics=topics_list, categories=categories)
    except Exception as e:
        current_app.logger.error(f"Error fetching topics: {str(e)}")
        return render_template('admin/topics.html', topics=[], categories=[])
    
    

@admin_bp.route('/add_topic', methods=['POST'])
@admin_token_required
def add_topic():
    try:
        # Validate required fields
        title = request.form.get('title')
        category = request.form.get('category')
        report_file = request.files.get('report')
        
        if not title or not category:
            return jsonify({
                "success": False,
                "message": "Title and category are required fields!"
            }), 400
        
        if not report_file or not allowed_file1(report_file.filename):
            return jsonify({
                "success": False,
                "message": "Valid report file (PDF/DOC/DOCX) is required!"
            }), 400
        
        # Generate topic_id
        last_topic = mongo.db.topics.find_one(sort=[("topic_id", -1)])
        topic_id = str(int(last_topic["topic_id"]) + 1) if last_topic else "1001"
        
        # Handle file upload using save_file function
        report_filename = save_file1(report_file, 'reports')
        
        if not report_filename:
            return jsonify({
                "success": False,
                "message": "Error saving report file!"
            }), 500
        
        # Create topic document
        topic_data = {
            "topic_id": topic_id,
            "project_name": title,
            "year": request.form.get('year', 'IEEE-2023'),
            "report": report_filename,
            "category": category,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert into database
        result = mongo.db.topics.insert_one(topic_data)
        
        return jsonify({
            "success": True,
            "message": "Topic added successfully!",
            "topic_id": topic_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error adding topic: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error adding topic: {str(e)}"
        }), 500

@admin_bp.route('/delete_topic/<topic_id>', methods=['DELETE'])
@admin_token_required
def delete_topic(topic_id):
    try:
        # Find the topic
        topic = mongo.db.topics.find_one({"topic_id": topic_id})
        if not topic:
            return jsonify({
                "success": False,
                "message": "Topic not found!"
            }), 404
        
        # Delete associated report file
        if topic.get('report'):
            report_path = os.path.join(
                current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), 
                'reports', 
                topic['report']
            )
            if os.path.exists(report_path):
                os.remove(report_path)
        
        # Delete from database
        result = mongo.db.topics.delete_one({"topic_id": topic_id})
        
        if result.deleted_count > 0:
            return jsonify({
                "success": True,
                "message": "Topic deleted successfully!"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to delete topic!"
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error deleting topic: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error deleting topic: {str(e)}"
        }), 500


@admin_bp.route('/download_report/<path:filename>')
def download_report(filename):
    try:
        # filename comes as 'uploads/reports/xxxx_file.pdf' from DB
        file_path = os.path.join('static', filename)
        # Extract just the base filename for the download name
        base_name = os.path.basename(filename)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=base_name
        )
    except Exception as e:
        current_app.logger.error(f"Error downloading report: {str(e)}")
        return jsonify({"error": "File not found"}), 404



@admin_bp.route('/viewmails', methods=['GET'])
@admin_token_required
def viewmails():
    """Admin add_projects - protected route."""
    Mails = list(mongo.db.contact.find())
    # print(Mails)
    return render_template('admin/viewmails.html',Mails=Mails)


@admin_bp.route('/delete-mail/<mail_id>', methods=['DELETE'])
@admin_token_required  # Uncomment if you have authentication
def delete_mail(mail_id):
    """Delete a contact mail message with enhanced error handling"""
    try:
        # Validate input
        if not mail_id or not mail_id.strip():
            return jsonify({
                'success': False,
                'message': 'Mail ID is required'
            }), 400

        # Validate ObjectId format
        if not ObjectId.is_valid(mail_id):
            return jsonify({
                'success': False,
                'message': 'Invalid mail ID format'
            }), 400

        # Check if mail exists before deleting
        existing_mail = mongo.db.contact.find_one({'_id': ObjectId(mail_id)})
        if not existing_mail:
            return jsonify({
                'success': False,
                'message': 'Mail not found'
            }), 404

        # Delete the mail
        result = mongo.db.contact.delete_one({'_id': ObjectId(mail_id)})
        
        if result.deleted_count == 1:
            print(f"Mail {mail_id} deleted successfully")
            return jsonify({
                'success': True,
                'message': 'Mail deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete mail'
            }), 500

    except Exception as e:
        print(f"Error deleting mail {mail_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An internal server error occurred'
        }), 500