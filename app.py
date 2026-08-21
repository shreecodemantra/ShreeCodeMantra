import os
from flask import Flask, render_template, send_from_directory, request, Response, make_response
from config import Config
from extensions import mongo, mail
from auth.routes import auth_bp
from admin.routes import admin_bp
from users.routes import user_bp

app = Flask(__name__)

app.config.from_object(Config)
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=int(os.getenv('MAIL_PORT')),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't'),
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')
)

mongo.init_app(app)
mail.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route('/')
def home():
    return render_template("users/index.html")



@app.route('/robots.txt')
def robots():
    content = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /auth/logout\n\nSitemap: {request.url_root}sitemap.xml\n"
    return Response(content, mimetype="text/plain")

@app.route('/sitemap.xml')
def sitemap():
    import xml.etree.ElementTree as ET
    
    # Root element
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Helper to add url
    def add_url(loc, changefreq="monthly", priority="0.5"):
        url_el = ET.SubElement(urlset, "url")
        ET.SubElement(url_el, "loc").text = f"{request.url_root.rstrip('/')}{loc}"
        ET.SubElement(url_el, "changefreq").text = changefreq
        ET.SubElement(url_el, "priority").text = priority
        
    # Standard static routes
    add_url("/", "daily", "1.0")
    add_url("/users/aboutus", "monthly", "0.8")
    add_url("/users/services", "daily", "0.9")
    add_url("/users/topics", "weekly", "0.8")
    add_url("/users/contact", "monthly", "0.7")
    add_url("/users/blogs", "weekly", "0.8")
    
    # Dynamic routes from database (projects)
    try:
        projects = list(mongo.db.projects.find({}, {"slug": 1, "_id": 1}))
        for project in projects:
            slug_or_id = project.get("slug") or str(project["_id"])
            add_url(f"/users/project/{slug_or_id}", "weekly", "0.8")
    except Exception as e:
        app.logger.error(f"Error querying projects for sitemap: {e}")
        
    # Generate XML response
    xml_str = ET.tostring(urlset, encoding='utf-8', method='xml')
    xml_content = b'<?xml version="1.0" encoding="utf-8"?>\n' + xml_str
    
    response = make_response(xml_content)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('users/404.html'), 404

if __name__ == '__main__':
    # Use livereload for fast responsive hot-reloading during development
    try:
        from livereload import Server
        app.debug = True
        server = Server(app.wsgi_app)
        server.watch('templates/')
        server.watch('static/')
        print("Starting Livereload Server...")
        server.serve(port=5000, host="0.0.0.0")
    except ImportError:
        # Fallback to normal flask if livereload is not installed
        app.run("0.0.0.0", debug=True)