from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows cross-origin requests

credentials = [
    {"website": "facebook.com", "username": "fb_user", "password": "fb_pass"},
    {"website": "gmail.com", "username": "gmail_user", "password": "gmail_pass"},
    {"website": "linkedin.com", "username": "linkedin_user", "password": "linkedin_pass"}
]

@app.route('/credentials', methods=['GET'])
def get_credentials():
    return jsonify(credentials)

if __name__ == '__main__':
    app.run(debug=True)
