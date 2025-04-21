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