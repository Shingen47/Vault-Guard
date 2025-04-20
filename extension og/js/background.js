// Store credentials temporarily
let storedCredentials = null;

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "fetchCredentials") {
        console.log("Background script: Received request for website:", message.website);
        
        const requestBody = { website: message.website };
        console.log("Background script: Sending request to backend:", requestBody);
        
        // Use XMLHttpRequest instead of fetch for better CORS handling
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "http://127.0.0.1:5000/get-credentials-extension", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        
        xhr.onload = function() {
            console.log("Background script: Response status:", xhr.status);
            if (xhr.status === 200) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    console.log("Background script: Response data:", data);
                    
                    if (data.credentials && data.credentials.length > 0) {
                        console.log("Background script: Found credentials:", data.credentials);
                        sendResponse({ credentials: data.credentials });
                    } else {
                        console.log("Background script: No credentials found in response");
                        sendResponse({ error: "No credentials found" });
                    }
                } catch (e) {
                    console.error("Background script: Error parsing response:", e);
                    sendResponse({ error: "Error parsing response from server" });
                }
            } else {
                console.error("Background script: Error response from backend:", xhr.status);
                sendResponse({ error: "Error response from backend: " + xhr.status });
            }
        };
        
        xhr.onerror = function() {
            console.error("Background script: Network error");
            sendResponse({ error: "Failed to connect to the backend. Make sure the Flask server is running." });
        };
        
        xhr.send(JSON.stringify(requestBody));
        
        // Return true to indicate that the response will be sent asynchronously
        return true;
    }
    
    // Handle authentication requests
    else if (message.action === "authenticate") {
        console.log("Background script: Received authentication request with method:", message.method);
        
        // Use XMLHttpRequest for authentication
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "http://127.0.0.1:5000/authenticate", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        
        xhr.onload = function() {
            console.log("Background script: Authentication response status:", xhr.status);
            if (xhr.status === 200) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    console.log("Background script: Authentication response:", data);
                    
                    if (data.message && data.message.includes("successful")) {
                        console.log("Background script: Authentication successful");
                        sendResponse({ success: true });
                    } else {
                        console.error("Background script: Authentication failed:", data.error);
                        sendResponse({ success: false, error: data.error || "Authentication failed" });
                    }
                } catch (e) {
                    console.error("Background script: Error parsing authentication response:", e);
                    sendResponse({ success: false, error: "Error parsing authentication response" });
                }
            } else {
                console.error("Background script: Authentication error response:", xhr.status);
                sendResponse({ success: false, error: "Authentication error: " + xhr.status });
            }
        };
        
        xhr.onerror = function() {
            console.error("Background script: Authentication network error");
            sendResponse({ success: false, error: "Failed to connect to the authentication server" });
        };
        
        xhr.send(JSON.stringify({ method: message.method }));
        
        // Return true to indicate that the response will be sent asynchronously
        return true;
    }

    // Handle autofill requests
    else if (message.action === "autofill") {
        console.log("Background script: Received autofill request");
        
        // Get the active tab
        chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            if (tabs.length === 0) {
                sendResponse({ success: false, error: "No active tab found" });
                return;
            }
            
            const activeTab = tabs[0];
            console.log("Background script: Active tab:", activeTab.url);
            
            // Send a message to the content script to fill the fields
            chrome.tabs.sendMessage(activeTab.id, {
                action: "fillFields",
                username: message.username,
                password: message.password
            }, function(response) {
                console.log("Background script: Content script response:", response);
                sendResponse({ success: true });
            });
        });
        
        // Return true to indicate that the response will be sent asynchronously
        return true;
    }
});