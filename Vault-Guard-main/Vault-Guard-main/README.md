# VaultGuard - Secure Password Manager

VaultGuard is a secure password manager that uses honey encryption to protect your passwords. It displays fake data to unauthorized users while keeping your real passwords secure.

## Features

- **Honey Encryption**: Displays realistic-looking fake data to unauthorized users
- **Secure Storage**: Passwords are encrypted using AES-256 encryption
- **Multi-Platform Support**: Works on Windows and macOS
- **Multiple Authentication Methods**:
  - Master Password
  - Windows Hello PIN Authentication
  - TouchID (macOS)
- **Password Management**:
  - Add, edit, and delete passwords
  - Organize passwords by categories
  - Generate strong passwords
  - Check password strength
- **Secure Notes**: Store encrypted notes
- **2FA Support**: Set up two-factor authentication
- **Password History**: Track password changes
- **Security Audit**: Analyze password strength and security

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/VaultGuard.git
cd VaultGuard
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the backend directory with:
```
MONGO_URI=mongodb://localhost:27017
SECRET_KEY=your_secret_key
KEY=your_encryption_key
IV=your_initialization_vector
```

4. Start the server:
```bash
python app.py
```

## Usage

1. Open your browser and navigate to `http://localhost:5000`
2. Choose your preferred authentication method:
   - Master Password
   - Windows Hello PIN
   - TouchID (macOS)
3. Start managing your passwords securely

## Security Features

- **Honey Encryption**: Realistic fake data shown to unauthorized users
- **AES-256 Encryption**: Military-grade encryption for stored passwords
- **Secure Authentication**: Multiple authentication methods
- **No Plaintext Storage**: Passwords are never stored in plaintext
- **Automatic Logout**: Session timeout for security

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Honey Encryption concept by Ari Juels and Thomas Ristenpart
- Flask for the web framework
- MongoDB for database storage
- Windows Hello API for secure authentication

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