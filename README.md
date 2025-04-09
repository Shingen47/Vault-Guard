# VaultGuard - Secure Password Manager

A secure password manager with browser extension for autofilling credentials.

## Project Structure

```
.
├── extension/                  # Browser extension files
│   ├── js/                     # JavaScript files
│   │   ├── background.js        # Background script for extension
│   │   ├── content.js           # Content script for webpage interaction
│   │   └── popup.js             # Popup script for extension UI
│   ├── css/                     # CSS files
│   │   └── popup.css            # Styles for extension popup
│   ├── html/                    # HTML files
│   │   └── popup.html           # Extension popup UI
│   ├── icon.png                 # Extension icon
│   └── manifest.json            # Extension manifest
│
├── backend/                     # Backend server files
│   ├── app.py                   # Main Flask application
│   ├── database.json            # Credentials database
│   ├── .env                     # Environment variables
│   ├── utils/                   # Utility scripts
│   │   ├── add_credentials.py   # Script to add credentials
│   │   └── check_db.py          # Script to check database
│   └── tests/                   # Test files
│       └── test_backend.py       # Backend tests
│
├── static/                      # Static files for web interface
├── templates/                   # HTML templates for web interface
└── README.md                    # Project documentation
```

## Setup and Installation

1. Install the required Python packages:
   ```
   pip3 install -r backend/requirements.txt
   ```

2. Start the Flask backend server:
   ```
   python3 backend/app.py
   ```

3. Load the extension in your browser:
   - Open Firefox
   - Go to Extensions page
   - Enable Developer mode
   - Click "Load unpacked" and select the `extension` folder

## Usage

1. Click the VaultGuard extension icon in your browser
2. Select a website from the dropdown
3. Click "Fetch Credentials" to retrieve stored credentials
4. Use the "Go To VaultGuard" button to access the web interface

## Security

- Credentials are stored in an encrypted database
- Authentication is required to access credentials
- The extension only works on specified domains