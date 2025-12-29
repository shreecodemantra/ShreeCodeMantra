from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from urllib.parse import quote_plus

username = "admin"
password = "UnknownHacker@2000"
password_encoded = quote_plus(password)

client = MongoClient(f"mongodb://{username}:{password_encoded}@localhost:27017/shreecodemantra?authSource=admin")
db = client["shreecodemantra"]

db.admin.insert_one({
    "name": "shree mantra",
    "email": "shreecodemantra@gmail.com",
    "password": generate_password_hash(password),
    "role": "admin"
})

print("✅ Admin user added successfully to 'shreecodemantra.admin'")
