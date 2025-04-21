import pymongo
from pprint import pprint
from app import encrypt_password, decrypt_password
from tabulate import tabulate
import sys
import random
from datetime import datetime

def generate_fake_data(count=10):
    websites = ['amazon.com', 'ebay.com', 'spotify.com', 'dropbox.com', 'slack.com', 
                'zoom.us', 'discord.com', 'reddit.com', 'pinterest.com', 'tumblr.com']
    categories = ['Personal', 'Work', 'Social', 'Shopping', 'Entertainment']
    email_domains = ['@gmail.com', '@yahoo.com', '@hotmail.com', '@outlook.com']
    
    fake_entries = []
    for _ in range(count):
        website = random.choice(websites)
        username = f"user{random.randint(1000, 9999)}{random.choice(email_domains)}"
        password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?', k=12))
        category = random.choice(categories)
        created_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        fake_entries.append({
            'website': website,
            'username': username,
            'password': password,
            'category': category,
            'createdAt': created_at,
            'is_fake': True
        })
    
    return fake_entries

def print_data(title, data, limit=20):
    print("\n" + "="*120)
    print(f"{title}")
    print("="*120)
    
    if not data:
        print("No data found!")
        return
        
    # Prepare data for tabulate
    table_data = []
    for entry in data[:limit]:  # Now showing up to 20 entries
        try:
            decrypted = decrypt_password(entry['password']) if 'password' in entry else "[Encrypted]"
        except:
            decrypted = "[Encrypted]"
            
        table_data.append([
            entry['website'],
            entry['username'],
            decrypted,
            entry.get('category', 'N/A'),
            entry.get('createdAt', 'N/A'),
            "FAKE" if entry.get('is_fake') else "REAL"
        ])
    
    # Print the table
    print(tabulate(table_data, 
                  headers=["Website", "Username", "Password", "Category", "Created At", "Type"],
                  tablefmt="grid",
                  numalign="left",
                  stralign="left"))
    print(f"\nShowing {len(table_data)} of {len(data)} total entries")
    print("="*120)

try:
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["vaultguard"]
    
    # Generate and insert 10 new fake entries
    print("\nGenerating 10 new fake entries...")
    new_fake_entries = generate_fake_data(10)
    db["fake_passwords"].insert_many(new_fake_entries)
    print("Successfully added 10 new fake entries!")
    
    # Get and display fake data
    fake_data = list(db["fake_passwords"].find({}))
    print_data("FAKE DATA TABLE (Honey Encryption)", fake_data)
    
    # Get and display real data
    real_data = list(db["passwords"].find({}))
    print_data("REAL DATA TABLE", real_data)

except Exception as e:
    print(f"An error occurred: {str(e)}")
    sys.exit(1) 