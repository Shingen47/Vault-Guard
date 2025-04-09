document.addEventListener("DOMContentLoaded", function () {
    const siteSelect = document.getElementById("site-select");
    const autofillBtn = document.getElementById("autofill-btn");
    const output = document.getElementById("output");

    // Populate the site dropdown with the current tab's domain
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
        const url = new URL(tabs[0].url);
        const domain = url.hostname;
        console.log("Current domain:", domain);
        
        let option = document.createElement("option");
        option.value = domain;
        option.textContent = domain;
        siteSelect.appendChild(option);
    });

    // Autofill when button is clicked
    autofillBtn.addEventListener("click", function() {
        const selectedSite = siteSelect.value;
        if (!selectedSite) {
            alert("Please select a website.");
            return;
        }
    
        // Normalize the website name (remove "www." and protocol)
        const normalizedSite = selectedSite.replace("www.", "").replace("https://", "").replace("http://", "");
        console.log("Attempting to fetch credentials for:", normalizedSite);
        
        // Clear previous results
        output.innerHTML = "";
        output.textContent = "Loading credentials...";
    
        // Send a message to the background script to fetch credentials
        chrome.runtime.sendMessage({ 
            action: "fetchCredentials", 
            website: normalizedSite 
        }, function(response) {
            console.log("Response received in popup:", response);
            
            if (response.credentials && response.credentials.length > 0) {
                output.innerHTML = ""; // Clear loading message
                response.credentials.forEach((cred) => {
                    const credDiv = document.createElement("div");
                    credDiv.className = "credential-item";
                    credDiv.innerHTML = `
                        <div>Username: ${cred.username}</div>
                        <div>Password: ${cred.password}</div>
                    `;
                    output.appendChild(credDiv);
                });
            } else {
                const errorMsg = response.error || "No credentials found.";
                console.error("Error:", errorMsg);
                output.textContent = errorMsg;
            }
        });
    });
});