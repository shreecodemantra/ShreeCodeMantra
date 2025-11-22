from flask import Flask, render_template,send_from_directory
from config import Config
from extensions import mongo, mail
from auth.routes import auth_bp
from admin.routes import admin_bp
from users.routes import user_bp

app = Flask(__name__)

app.config.from_object(Config)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='shreecodemantra@gmail.com',
    MAIL_PASSWORD='gosn rcxe xpef trcu',
    MAIL_DEFAULT_SENDER='shreecodemantra@gmail.com'  # 👈 Add this line
)

mongo.init_app(app)
mail.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route('/')
def home():
    return render_template("users/index.html")

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('.', 'sitemap.xml')

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
    # app.run("0.0.0.0")