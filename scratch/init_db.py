from pymongo import MongoClient

# Assuming default localhost connection and 'codemantra' DB based on typical setup
client = MongoClient('mongodb://localhost:27017/')
db = client.shreecodemantra

try:
    db.projects.create_index("slug", unique=True)
    print("Successfully created unique index on 'slug' in 'projects' collection.")
except Exception as e:
    print(f"Error creating index: {e}")
