// Listen for messages from the background script
browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "fillFields") {
        console.log("Content script: Received fillFields request");
        
        // Find username and password fields
        const usernameField = document.querySelector("input[type='text'], input[type='email'], input[name='username'], input[name='email'], input[id='username'], input[id='email']");
        const passwordField = document.querySelector("input[type='password'], input[name='password'], input[id='password']");
        
        if (usernameField && passwordField) {
            console.log("Content script: Found login fields, filling with provided credentials");
            
            // Fill the fields
            usernameField.value = message.username;
            passwordField.value = message.password;
            
            // Trigger input events to ensure any listeners are notified
            usernameField.dispatchEvent(new Event('input', { bubbles: true }));
            passwordField.dispatchEvent(new Event('input', { bubbles: true }));
            
            // Send success response
            sendResponse({ success: true, message: "Fields filled successfully" });
        } else {
            console.warn("Content script: Could not find login fields");
            sendResponse({ success: false, error: "Login fields not found on this page" });
        }
        
        // Return true to indicate that the response will be sent asynchronously
        return true;
    }
});

// Function to detect successful login
function detectSuccessfulLogin() {
    // Common indicators of successful login
    const successIndicators = [
        // URL changes that often indicate successful login
        window.location.href.includes('/dashboard'),
        window.location.href.includes('/account'),
        window.location.href.includes('/profile'),
        window.location.href.includes('/home'),
        
        // Common elements that appear after login
        document.querySelector('.user-profile'),
        document.querySelector('.account-details'),
        document.querySelector('.welcome-message'),
        
        // Common text that appears after login
        document.body.innerText.includes('Welcome back'),
        document.body.innerText.includes('My Account'),
        document.body.innerText.includes('Dashboard')
    ];
    
    // Check if any of the indicators are present
    return successIndicators.some(indicator => {
        if (typeof indicator === 'string') {
            return document.body.innerText.includes(indicator);
        }
        return !!indicator;
    });
}

// Function to capture credentials from the page
function captureCredentials() {
    console.log("Content script: Starting credential capture");
    
    // First try to find GitHub's specific login form
    const loginForm = document.querySelector('form[action*="/session"]');
    console.log("Content script: Found GitHub login form:", !!loginForm);
    
    if (loginForm) {
        // Find username and password fields within the login form
        const usernameField = loginForm.querySelector("input[name='login']");
        const passwordField = loginForm.querySelector("input[type='password'][name='password']");
        
        console.log("Content script: Found fields in GitHub form:", {
            usernameField: !!usernameField,
            passwordField: !!passwordField,
            usernameFieldType: usernameField ? usernameField.type : null,
            usernameFieldName: usernameField ? usernameField.name : null,
            usernameFieldId: usernameField ? usernameField.id : null,
            passwordFieldType: passwordField ? passwordField.type : null,
            passwordFieldName: passwordField ? passwordField.name : null,
            passwordFieldId: passwordField ? passwordField.id : null
        });
        
        if (usernameField && passwordField) {
            const username = usernameField.value;
            const password = passwordField.value;
            
            console.log("Content script: Found GitHub credentials:", {
                username: username ? "present" : "missing",
                password: password ? "present" : "missing"
            });
            
            if (username && password) {
                // Get the current website domain
                const website = window.location.hostname;
                console.log("Content script: Website domain:", website);
                
                // Send credentials to background script for storage
                browser.runtime.sendMessage({
                    action: "storeCredentials",
                    credentials: {
                        website: website,
                        username: username,
                        password: password
                    }
                }).then(response => {
                    console.log("Content script: Credentials stored successfully", response);
                }).catch(error => {
                    console.error("Content script: Error storing credentials", error);
                });
            } else {
                console.log("Content script: Missing GitHub username or password values");
            }
        } else {
            console.log("Content script: Could not find GitHub login fields in form");
        }
    } else {
        console.log("Content script: Could not find GitHub login form");
    }
}

// Set up a mutation observer to detect DOM changes that might indicate successful login
const observer = new MutationObserver((mutations) => {
    // Check if login was successful
    if (detectSuccessfulLogin()) {
        console.log("Content script: Detected successful login");
        
        // Wait a short time to ensure the page has fully loaded
        setTimeout(() => {
            captureCredentials();
        }, 1000);
        
        // Disconnect the observer since we've detected login
        observer.disconnect();
    }
});

// Start observing the document with the configured parameters
observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Also check for successful login on page load
document.addEventListener('DOMContentLoaded', () => {
    // Wait a short time to ensure the page has fully loaded
    setTimeout(() => {
        if (detectSuccessfulLogin()) {
            console.log("Content script: Detected successful login on page load");
            captureCredentials();
        }
    }, 2000);
});