let credentials = [];

async function fetchCredentials() {
    try {
        console.log("📡 Fetching credentials...");
        let response = await fetch("http://127.0.0.1:5000/credentials");

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        credentials = await response.json();
        console.log("📂 Retrieved credentials:", credentials);
    } catch (error) {
        console.error("❌ Error fetching credentials:", error);
    }
}

// Fetch credentials when the extension starts
fetchCredentials();

// Listen for messages from popup.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("📩 Message received:", request);

    if (request.action === "fetchCredentials") {
        console.log("📤 Sending credentials to popup.js:", credentials);
        sendResponse({ credentials: credentials });
    }

    if (request.action === "autofill") {
        let site = request.website;
        let cred = credentials.find(c => c.website.includes(site));

        if (cred) {
            console.log("🚀 Injecting autofill script for:", site);
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                if (tabs.length === 0) return;

                chrome.tabs.sendMessage(tabs[0].id, {
                    action: "fillFields",
                    username: cred.username,
                    password: cred.password
                });
            });
        } else {
            console.warn("⚠️ No credentials found for", site);
        }
    }
});
