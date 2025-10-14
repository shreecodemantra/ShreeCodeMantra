from flask import Flask, render_template
from config import Config
from extensions import mongo
from auth.routes import auth_bp
from admin.routes import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

mongo.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
@app.route('/')
def home():
    return render_template("main/index.html")

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
    # app.run("0.0.0.0")
