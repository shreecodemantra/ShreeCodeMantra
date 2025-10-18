from werkzeug.security import generate_password_hash
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["shreecodemanta"]

# Insert admin user
db.admin.insert_one({
    "name": "Yash Salvi",
    "email": "yash.salvi1209@gmail.com",
    "password": generate_password_hash("Yash@1234"),
    "role": "admin"
})

print("✅ Admin user added successfully to 'shreecodemanta.users'")
