import pymongo
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Connect to MongoDB
client = pymongo.MongoClient(os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017"))
db = client["vaultguard"]
passwords_collection = db["passwords"]

# Get all credentials
credentials = list(passwords_collection.find({}, {"_id": 0}))

print(f"Found {len(credentials)} credentials in the database:")
for cred in credentials:
    print(f"Website: {cred.get('website')}, Username: {cred.get('username')}") 