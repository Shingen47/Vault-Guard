from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, session
from flask_cors import CORS
import touchid
import os
from datetime import datetime, timedelta
from time import time
import hashlib
import pymongo
from bson.objectid import ObjectId
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from dotenv import load_dotenv
import secrets
import string
import re
import pyotp
import io
import base64
import qrcode
from collections import defaultdict

load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Add this line for session support
# Configure CORS to allow all origins for extension requests
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

# Connect to MongoDB
client = pymongo.MongoClient(
    os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017"))
db = client["vaultguard"]
passwords_collection = db["passwords"]
notes_collection = db["secure_notes"]
categories_collection = db["categories"]
password_history_collection = db["password_history"]
user_settings_collection = db["user_settings"]

# AES Encryption Setup
SECRET_KEY = os.getenv("SECRET_KEY")
AES_PADDING = os.getenv("AES_PADDING")
KEY = os.getenv("KEY").encode()
IV = os.getenv("IV").encode()

# Password strength criteria
PASSWORD_CRITERIA = {
    "min_length": 8,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_numbers": True,
    "require_special": True
}

def encrypt_password(password):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    ciphertext = cipher.encrypt(pad(password.encode('utf-8'), AES.block_size))
    return ciphertext.hex()  # Store as a hex string in MongoDB


def decrypt_password(encrypted_password_hex):
    try:
        encrypted_password = bytes.fromhex(
            encrypted_password_hex)  # Convert back from hex
        decipher = AES.new(KEY, AES.MODE_CBC, IV)
        plaintext = unpad(decipher.decrypt(
            encrypted_password), AES.block_size).decode()
        return plaintext
    except Exception as e:
        return str(e)



MASTER_PASSWORD_FILE = "master.txt"


def load_master_password():
    if os.path.exists(MASTER_PASSWORD_FILE):
        with open(MASTER_PASSWORD_FILE, "r") as f:
            return f.read().strip()
    else:
        master_password = hashlib.sha256(
            input("Set a master password: ").encode()).hexdigest()
        with open(MASTER_PASSWORD_FILE, "w") as f:
            f.write(master_password)
        return master_password


MASTER_PASSWORD = load_master_password()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/vault")
def vault():
    session_token = request.cookies.get("session_token")
    if session_token == MASTER_PASSWORD:
        passwords = list(passwords_collection.find(
            {}, {"_id": 0}))  # Exclude MongoDB `_id`
        for p in passwords:
            # Decrypt password before displaying
            p["password"] = decrypt_password(p["password"])
        return render_template("vault.html", passwords=passwords)
    else:
        return redirect(url_for("index"))


@app.route("/authenticate", methods=["POST"])
def authenticate():
    data = request.json
    method = data.get("method")

    if (method == "password"):
        entered_password = hashlib.sha256(
            data.get("password", "").encode()).hexdigest()
        if entered_password == MASTER_PASSWORD:
            response = make_response(
                jsonify({"message": "Authentication successful!"}), 200)
            response.set_cookie(
                "session_token", MASTER_PASSWORD, httponly=True, secure=True)
            return response
        return jsonify({"error": "Incorrect Master Password"}), 401

    elif (method == "touchid"):
        try:
            touchid.authenticate()
            response = make_response(
                jsonify({"message": "Touch ID authenticated!"}), 200)
            response.set_cookie(
                "session_token", MASTER_PASSWORD, httponly=True, secure=True)
            return response
        except Exception as e:
            return jsonify({"error": "Touch ID authentication failed", "details": str(e)}), 401


@app.route("/logout")
def logout():
    response = make_response(redirect(url_for("index")))
    # Explicitly setting path and expiry
    response.set_cookie("session_token", "", expires=0, path="/")
    return response


@app.route("/decrypt-password")
def decrypt_stored_password():
    encrypted_password = request.args.get("encrypted")
    try:
        decrypted_password = decrypt_password(encrypted_password)
        return jsonify({"password": decrypted_password})
    except Exception as e:
        return jsonify({"error": "Failed to decrypt password", "details": str(e)}), 500


@app.route("/get-passwords", methods=['GET'])
def get_passwords():
    passwords = list(passwords_collection.find({}, {"_id": 0})
                     )  # Exclude MongoDB's `_id` field
    for p in passwords:
        p["password"] = decrypt_password(p["password"])
    return jsonify({"passwords": passwords})


@app.route("/get-credentials-extension", methods=["POST"])
def get_credentials_extension():
    try:
        data = request.json
        if not data:
            print("Extension request - No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400
            
        website = data.get("website")
        if not website:
            print("Extension request - No website provided in request")
            return jsonify({"error": "Website is required"}), 400

        # Normalize the website name (remove "www." and protocol)
        normalized_website = website.replace("www.", "").replace("https://", "").replace("http://", "")
        print(f"Extension request - Normalized website: {normalized_website}")

        # Query the database for credentials matching the normalized website
        print(f"Extension request - Querying MongoDB for website: {normalized_website}")
        
        # Try exact match first
        credentials = list(passwords_collection.find({"website": normalized_website}, {"_id": 0}))
        
        # If no exact match, try partial match
        if not credentials:
            print(f"Extension request - No exact match, trying partial match")
            credentials = list(passwords_collection.find({"website": {"$regex": f".*{normalized_website}.*"}}, {"_id": 0}))
        
        print(f"Extension request - Raw MongoDB query result: {credentials}")
        
        # Decrypt passwords
        for p in credentials:
            p["password"] = decrypt_password(p["password"])
            
        print(f"Extension request - Found {len(credentials)} credentials")
        if credentials:
            print(f"Extension request - Returning credentials for {normalized_website}")
            return jsonify({"credentials": credentials}), 200
        else:
            print(f"Extension request - No credentials found for {normalized_website}")
            return jsonify({"error": "No credentials found for the specified website"}), 404
            
    except Exception as e:
        print(f"Extension request - Error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/retrieve-password")
def retrieve_password():
    website = request.args.get("website")
    method = ""
    entry = passwords_collection.find_one({"website": website}, {"_id": 0})
    if entry:
        try:
            touchid.authenticate()
            return jsonify({"password": decrypt_password(entry['password'])})
        except Exception as e:
            return jsonify({"error": "Website not found"}), 404


@app.route("/add-password", methods=["POST"])
def add_password():
    data = request.json
    print(data)

    encrypted_password = encrypt_password(
        data["password"])  # Encrypt before saving

    # Add to passwords collection
    passwords_collection.insert_one({
        "website": data["website"],
        "username": data["username"],
        "password": encrypted_password,
        "category": data.get("category", "General"),
        "createdAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "updatedAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })
    
    # Add to password history
    password_history_collection.insert_one({
        "website": data["website"],
        "username": data["username"],
        "password": encrypted_password,
        "changedAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

    return jsonify({"message": "Password saved successfully!"})


@app.route("/edit-password", methods=["POST"])
def edit_password():
    data = request.json
    website = data["website"]
    new_username = data["username"]
    new_password = encrypt_password(data["password"])
    newUpdatedAt = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    result = passwords_collection.update_one(
        {"website": website},
        {"$set": {"username": new_username,
                  "password": new_password, 
                  "updatedAt": newUpdatedAt,
                  "category": data.get("category", "General")}}
    )

    if result.modified_count > 0:
        # Add to password history
        password_history_collection.insert_one({
            "website": website,
            "username": new_username,
            "password": new_password,
            "changedAt": newUpdatedAt
        })
        return jsonify({"message": "Password updated successfully!"})
    else:
        return jsonify({"error": "Website not found!"}), 404


@app.route("/delete-password", methods=["POST"])
def delete_password():
    data = request.json
    website = data["website"]

    result = passwords_collection.delete_one({"website": website})

    if result.deleted_count > 0:
        return jsonify({"message": "Password deleted successfully!"})
    else:
        return jsonify({"error": "Website not found!"}), 404


# New functions for password generation and strength checking
def generate_password(length=16, include_uppercase=True, include_lowercase=True, include_numbers=True, include_special=True):
    """Generate a secure password based on specified criteria"""
    chars = ""
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_lowercase:
        chars += string.ascii_lowercase
    if include_numbers:
        chars += string.digits
    if include_special:
        chars += string.punctuation
    
    if not chars:
        chars = string.ascii_letters + string.digits + string.punctuation
    
    password = ''.join(secrets.choice(chars) for _ in range(length))
    return password

def check_password_strength(password):
    """Check password strength and return a score from 0-100"""
    score = 0
    
    # Length check
    if len(password) >= 12:
        score += 25
    elif len(password) >= 8:
        score += 15
    
    # Character type checks
    if re.search(r'[A-Z]', password):
        score += 20
    if re.search(r'[a-z]', password):
        score += 20
    if re.search(r'[0-9]', password):
        score += 20
    if re.search(r'[^A-Za-z0-9]', password):
        score += 20
    
    # Entropy check
    unique_chars = len(set(password))
    if unique_chars >= 12:
        score += 10
    
    return min(score, 100)

def is_password_expired(updated_at, expiration_days=90):
    """Check if a password has expired based on its last update date"""
    if not updated_at:
        return True
    
    try:
        update_date = datetime.strptime(updated_at, "%d/%m/%Y %H:%M:%S")
        expiration_date = update_date + timedelta(days=expiration_days)
        return datetime.now() > expiration_date
    except:
        return True

# New routes for additional features
@app.route("/generate-password", methods=["POST"])
def generate_secure_password():
    data = request.json
    length = data.get("length", 16)
    include_uppercase = data.get("include_uppercase", True)
    include_lowercase = data.get("include_lowercase", True)
    include_numbers = data.get("include_numbers", True)
    include_special = data.get("include_special", True)
    
    password = generate_password(
        length=length,
        include_uppercase=include_uppercase,
        include_lowercase=include_lowercase,
        include_numbers=include_numbers,
        include_special=include_special
    )
    
    strength = check_password_strength(password)
    
    return jsonify({
        "password": password,
        "strength": strength
    })

@app.route("/check-password-strength", methods=["POST"])
def check_strength():
    data = request.json
    password = data.get("password", "")
    
    strength = check_password_strength(password)
    feedback = []
    
    if len(password) < PASSWORD_CRITERIA["min_length"]:
        feedback.append(f"Password should be at least {PASSWORD_CRITERIA['min_length']} characters long")
    if PASSWORD_CRITERIA["require_uppercase"] and not re.search(r'[A-Z]', password):
        feedback.append("Password should contain at least one uppercase letter")
    if PASSWORD_CRITERIA["require_lowercase"] and not re.search(r'[a-z]', password):
        feedback.append("Password should contain at least one lowercase letter")
    if PASSWORD_CRITERIA["require_numbers"] and not re.search(r'[0-9]', password):
        feedback.append("Password should contain at least one number")
    if PASSWORD_CRITERIA["require_special"] and not re.search(r'[^A-Za-z0-9]', password):
        feedback.append("Password should contain at least one special character")
    
    return jsonify({
        "strength": strength,
        "feedback": feedback
    })

@app.route("/categories", methods=["GET"])
def get_categories():
    categories = list(categories_collection.find({}, {"_id": 0}))
    return jsonify({"categories": categories})

@app.route("/add-category", methods=["POST"])
def add_category():
    data = request.json
    name = data.get("name")
    color = data.get("color", "#6366f1")
    
    if not name:
        return jsonify({"error": "Category name is required"}), 400
    
    # Check if category already exists
    existing = categories_collection.find_one({"name": name})
    if existing:
        return jsonify({"error": "Category already exists"}), 400
    
    categories_collection.insert_one({
        "name": name,
        "color": color,
        "createdAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })
    
    return jsonify({"message": "Category added successfully"})

@app.route("/secure-notes", methods=["GET"])
def get_secure_notes():
    notes = list(notes_collection.find({}, {"_id": 0}))
    for note in notes:
        note["content"] = decrypt_password(note["content"])
    return jsonify({"notes": notes})

@app.route("/add-note", methods=["POST"])
def add_secure_note():
    data = request.json
    title = data.get("title")
    content = data.get("content")
    category = data.get("category", "General")
    
    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400
    
    encrypted_content = encrypt_password(content)
    
    notes_collection.insert_one({
        "title": title,
        "content": encrypted_content,
        "category": category,
        "createdAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "updatedAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })
    
    return jsonify({"message": "Note added successfully"})

@app.route("/edit-note", methods=["POST"])
def edit_secure_note():
    data = request.json
    note_id = data.get("id")
    title = data.get("title")
    content = data.get("content")
    category = data.get("category", "General")
    
    if not note_id or not title or not content:
        return jsonify({"error": "ID, title and content are required"}), 400
    
    encrypted_content = encrypt_password(content)
    
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {
            "title": title,
            "content": encrypted_content,
            "category": category,
            "updatedAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }}
    )
    
    if result.modified_count > 0:
        return jsonify({"message": "Note updated successfully"})
    else:
        return jsonify({"error": "Note not found"}), 404

@app.route("/delete-note", methods=["POST"])
def delete_secure_note():
    data = request.json
    note_id = data.get("id")
    
    if not note_id:
        return jsonify({"error": "Note ID is required"}), 400
    
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})
    
    if result.deleted_count > 0:
        return jsonify({"message": "Note deleted successfully"})
    else:
        return jsonify({"error": "Note not found"}), 404

@app.route("/setup-2fa", methods=["POST"])
def setup_2fa():
    # Generate a new secret key
    secret_key = pyotp.random_base32()
    
    # Create a TOTP object
    totp = pyotp.TOTP(secret_key)
    
    # Generate the QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp.provisioning_uri("VaultGuard", issuer_name="VaultGuard"))
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_code = base64.b64encode(buffered.getvalue()).decode()
    
    # Store the secret key in user settings
    user_settings_collection.update_one(
        {"type": "2fa"},
        {"$set": {"secret_key": secret_key, "enabled": False}},
        upsert=True
    )
    
    return jsonify({
        "qr_code": f"data:image/png;base64,{qr_code}",
        "secret_key": secret_key
    })

@app.route("/verify-2fa", methods=["POST"])
def verify_2fa():
    data = request.json
    code = data.get("code")
    
    if not code:
        return jsonify({"error": "Verification code is required"}), 400
    
    # Get the secret key from user settings
    settings = user_settings_collection.find_one({"type": "2fa"})
    if not settings or not settings.get("secret_key"):
        return jsonify({"error": "2FA not set up"}), 400
    
    # Create TOTP object
    totp = pyotp.TOTP(settings["secret_key"])
    
    # Verify the code
    if totp.verify(code):
        # Enable 2FA
        user_settings_collection.update_one(
            {"type": "2fa"},
            {"$set": {"enabled": True}},
            upsert=True
        )
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Invalid verification code"}), 400

@app.route("/check-2fa-status", methods=["GET"])
def check_2fa_status():
    settings = user_settings_collection.find_one({"type": "2fa"})
    return jsonify({
        "enabled": settings.get("enabled", False) if settings else False
    })

@app.route("/password-history", methods=["GET"])
def get_password_history():
    website = request.args.get("website")
    
    if not website:
        return jsonify({"error": "Website is required"}), 400
    
    history = list(password_history_collection.find(
        {"website": website},
        {"_id": 0}
    ).sort("changedAt", -1))
    
    for entry in history:
        entry["password"] = decrypt_password(entry["password"])
    
    return jsonify({"history": history})

@app.route('/security-audit', methods=['POST'])
def security_audit():
    """Perform security audit of stored passwords."""
    try:
        # Get all passwords from database since we don't have user sessions yet
        passwords = list(passwords_collection.find({}))
        
        # Decrypt passwords for analysis
        for password in passwords:
            if 'password' in password:
                password['password'] = decrypt_password(password['password'])
        
        # Analyze passwords
        issues = []
        recommendations = []
        
        # Check for weak passwords
        weak_passwords = [p for p in passwords if check_password_strength(p.get('password', '')) < 70]
        if weak_passwords:
            issues.append({
                'title': 'Weak Passwords',
                'description': f'{len(weak_passwords)} passwords are below recommended strength'
            })
            recommendations.append({
                'title': 'Update Weak Passwords',
                'description': 'Use the password generator to create stronger passwords'
            })
        
        # Check for duplicate passwords
        password_counts = defaultdict(list)
        for p in passwords:
            if 'password' in p:
                password_counts[p['password']].append(p.get('website', 'Unknown'))
        
        duplicates = {pwd: sites for pwd, sites in password_counts.items() if len(sites) > 1}
        if duplicates:
            issues.append({
                'title': 'Duplicate Passwords',
                'description': f'{len(duplicates)} passwords are used across multiple accounts'
            })
            recommendations.append({
                'title': 'Change Duplicate Passwords',
                'description': 'Use unique passwords for each account'
            })
        
        # Check for old passwords
        old_passwords = [p for p in passwords if is_password_expired(p.get('updatedAt'))]
        if old_passwords:
            issues.append({
                'title': 'Old Passwords',
                'description': f'{len(old_passwords)} passwords haven\'t been changed in over 90 days'
            })
            recommendations.append({
                'title': 'Update Old Passwords',
                'description': 'Regularly update your passwords to maintain security'
            })
        
        # Calculate security score
        total_passwords = len(passwords)
        if total_passwords == 0:
            score = 100
        else:
            weak_score = len(weak_passwords) / total_passwords * 100
            duplicate_score = len(duplicates) / total_passwords * 100
            old_score = len(old_passwords) / total_passwords * 100
            score = 100 - (weak_score + duplicate_score + old_score) / 3
            score = max(0, min(100, score))  # Ensure score is between 0 and 100
        
        return jsonify({
            'score': round(score),
            'issues': issues,
            'recommendations': recommendations
        })
        
    except Exception as e:
        print(f"Error in security audit: {str(e)}")
        return jsonify({'error': 'Failed to perform security audit'}), 500

@app.route("/store-credentials", methods=["POST"])
def store_credentials():
    try:
        data = request.get_json()
        username = data.get("username")
        encrypted_password = data.get("password")  # Password is already encrypted by the extension
        website = data.get("website")
        
        if not all([username, encrypted_password, website]):
            return jsonify({"error": "Missing required fields"}), 400
            
        # Check if credentials already exist for this website
        existing_cred = passwords_collection.find_one({"website": website})
        
        if existing_cred:
            # Update existing credentials
            passwords_collection.update_one(
                {"website": website},
                {
                    "$set": {
                        "username": username,
                        "password": encrypted_password,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            # Insert new credentials
            passwords_collection.insert_one({
                "username": username,
                "password": encrypted_password,
                "website": website,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
        return jsonify({"message": "Credentials stored successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
