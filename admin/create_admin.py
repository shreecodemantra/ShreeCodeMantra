import sys
import os
from werkzeug.security import generate_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Add parent directory to sys.path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def create_admin():
    try:
        # Use the URI from config.py
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        
        db = client["shreecodemantra"]
        
        admin_data = {
            "name": os.getenv("ADMIN_NAME"),
            "email": os.getenv("ADMIN_EMAIL"),
            "password": generate_password_hash(os.getenv("ADMIN_PASSWORD")),
            "role": os.getenv("ADMIN_ROLE")
        }
        
        result = db.admin.update_one(
            {"email": admin_data["email"]},
            {"$set": admin_data},
            upsert=True
        )
        
        if result.upserted_id:
            print(f"[SUCCESS] Admin user created successfully (ID: {result.upserted_id})")
        else:
            print("[SUCCESS] Admin user updated successfully")
            
        # Configure query performance indexes
        db.projects.create_index([("slug", 1)], unique=True, sparse=True)
        db.projects.create_index([("category", 1)])
        db.projects.create_index([("upload_date", -1)])
        db.topics.create_index([("topic_id", 1)], unique=True)
        db.topics.create_index([("created_at", -1)])
        print("[SUCCESS] Performance query indexes initialized successfully")
            
    except OperationFailure as e:
        print(f"[ERROR] Authentication failed: {e}")
        print("Please check if the MONGO_URI in config.py is correct for your local MongoDB instance.")
    except ConnectionFailure as e:
        print(f"[ERROR] Could not connect to MongoDB: {e}")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    create_admin()
