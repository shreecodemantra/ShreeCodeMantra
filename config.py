import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/shreecodemantra")
    SECRET_KEY = os.getenv("SECRET_KEY", "Shree@1122")

