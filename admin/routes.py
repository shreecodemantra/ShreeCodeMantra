from flask import Blueprint, render_template, request, jsonify, make_response, current_app, send_from_directory
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from extensions import mongo
from auth.auth_utils import create_jwt_token, token_required
import os
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', '7z'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, subfolder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', UPLOAD_FOLDER), subfolder)
        os.makedirs(upload_path, exist_ok=True)
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
        admin_user = mongo.db.users.find_one({'email': email, 'role': 'admin'})

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
                max_age=2 * 60 * 60  # 2 hours
            )
            return resp

        return jsonify({"status": "fail", "error": "Invalid admin credentials!"})

    return render_template('admin/admin-login.html')

@admin_bp.route('/dashboard', methods=['GET'])
# @token_required
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
    resp.delete_cookie("admin_token")
    return resp

@admin_bp.route('/add_projects', methods=['GET'])
# @token_required
def add_projects():
    """Admin add_projects - protected route."""
    categories = list(mongo.db.categories.find())
    return render_template('admin/add_projects.html', categories=categories)

@admin_bp.route('/add_project', methods=['POST'])
# @token_required
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
# @token_required
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
# @token_required
def get_categories():
    categories = list(mongo.db.categories.find({}, {'_id': 0, 'name': 1}))
    return jsonify(categories)

@admin_bp.route('/projects')
# @token_required
def view_projects():
    projects = list(mongo.db.projects.find())
    return render_template('admin/projects.html', projects=projects)

@admin_bp.route('/categories')
# @token_required
def view_categories():
    categories = list(mongo.db.categories.find())
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)