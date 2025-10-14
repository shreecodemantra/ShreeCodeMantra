from werkzeug.security import generate_password_hash
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["shreecodemanta"]

# Insert admin user
db.users.insert_one({
    "name": "Admin User",
    "email": "admin@example.com",
    "password": generate_password_hash("admin123"),
    "role": "admin"
})

print("✅ Admin user added successfully to 'shreecodemanta.users'")
