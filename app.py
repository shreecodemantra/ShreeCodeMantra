from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["shree_code_mantra_db"]
users_collection = db["users"]

# Route for the main page
@app.route('/')
def home():
    return render_template('index.html')  # loads templates/index.html

# # Example route to handle form submission
# @app.route('/contact', methods=['POST'])
# def contact():
#     name = request.form.get('name')
#     email = request.form.get('email')
#     message = request.form.get('message')

#     # For now, just print to the console (later we’ll save to a database)
#     print(f"Received: {name}, {email}, {message}")

#     return jsonify({'status': 'success', 'message': 'Thanks for contacting us!'})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/onepage')
def onepage():
    return render_template('one-page.html')

@app.route('/registermenu')
def registermenu():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    phone = request.form.get('phone')
    gender = request.form.get('gender')

    # Validation check
    if password != confirm:
        return jsonify({'status': 'error', 'message': 'Passwords do not match!'}), 400

    # Check if email already exists
    existing_user = users_collection.find_one({'email': email})
    if existing_user:
        return jsonify({'status': 'error', 'message': 'Email already registered!'}), 400

    # Save to MongoDB
    user_data = {
        'fullname': fullname,
        'email': email,
        'password': password,  # (In real apps, hash the password!)
        'phone': phone,
        'gender': gender
    }
    users_collection.insert_one(user_data)

    print(f"✅ New user registered: {fullname}, {email}")

    return jsonify({'status': 'success', 'message': 'Registration successful!'})


if __name__ == '__main__':
    app.run(debug=True)
