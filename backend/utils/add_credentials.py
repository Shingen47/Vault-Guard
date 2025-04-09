import json

FILE_PATH = "database.json"

def save_credentials(credentials):
    with open(FILE_PATH, "w") as file:
        json.dump(credentials, file, indent=4)

def add_credential(website, username, password):
    try:
        with open(FILE_PATH, "r") as file:
            credentials = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        credentials = []

    # Add new credential
    credentials.append({"website": website, "username": username, "password": password})
    save_credentials(credentials)

# Add Facebook credentials manually
add_credential("facebook.com", "your-email@example.com", "yourSecurePassword")

print("Updated Credentials:", json.load(open(FILE_PATH)))
