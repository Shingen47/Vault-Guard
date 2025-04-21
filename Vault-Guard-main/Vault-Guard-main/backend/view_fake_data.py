import pymongo
from pprint import pprint

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["vaultguard"]
fake_data = list(db["fake_passwords"].find({}))

print(f"\nNumber of fake entries: {len(fake_data)}")
print("\nSample fake entries:")
for entry in fake_data[:5]:
    print("\n------------------------")
    print(f"Website: {entry['website']}")
    print(f"Username: {entry['username']}")
    print(f"Category: {entry['category']}")
    print(f"Created At: {entry['createdAt']}") 