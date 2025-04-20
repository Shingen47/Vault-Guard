document.addEventListener("DOMContentLoaded", function () {
    const siteSelect = document.getElementById("site-select");
    const autofillBtn = document.getElementById("autofill-btn");
    const output = document.getElementById("output");

    // Add some base styles to the output container
    output.style.maxHeight = "400px";
    output.style.overflowY = "auto";
    output.style.padding = "15px";
    output.style.backgroundColor = "rgba(15, 23, 42, 0.6)";
    output.style.borderRadius = "0.375rem";
    output.style.border = "1px solid #334155";

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
        
        // Create a header for the credentials
        const headerDiv = document.createElement("div");
        headerDiv.style.display = "flex";
        headerDiv.style.alignItems = "center";
        headerDiv.style.justifyContent = "space-between";
        headerDiv.style.marginBottom = "15px";
        headerDiv.style.paddingBottom = "10px";
        headerDiv.style.borderBottom = "1px solid #334155";
        
        const titleSpan = document.createElement("span");
        titleSpan.textContent = "Available Credentials";
        titleSpan.style.color = "#f8fafc";
        titleSpan.style.fontWeight = "600";
        titleSpan.style.fontSize = "16px";
        
        const countSpan = document.createElement("span");
        countSpan.style.color = "#94a3b8";
        countSpan.style.fontSize = "14px";
        countSpan.textContent = "Loading...";
        
        headerDiv.appendChild(titleSpan);
        headerDiv.appendChild(countSpan);
        output.appendChild(headerDiv);
        
        // Add loading indicator
        const loadingDiv = document.createElement("div");
        loadingDiv.style.display = "flex";
        loadingDiv.style.alignItems = "center";
        loadingDiv.style.justifyContent = "center";
        loadingDiv.style.padding = "20px";
        loadingDiv.style.color = "#94a3b8";
        loadingDiv.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 10px; animation: spin 1s linear infinite;">
                <path d="M12 4.75V6.25M12 17.75V19.25M19.25 12H17.75M6.25 12H4.75M16.5 16.5L15.5 15.5M8.5 8.5L7.5 7.5M16.5 7.5L15.5 8.5M8.5 15.5L7.5 16.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>Loading credentials...</span>
        `;
        output.appendChild(loadingDiv);
        
        // Add keyframe animation for the spinner
        const style = document.createElement('style');
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    
        // Send a message to the background script to fetch credentials
        chrome.runtime.sendMessage({ 
            action: "fetchCredentials", 
            website: normalizedSite 
        }, function(response) {
            console.log("Response received in popup:", response);
            
            // Remove loading indicator
            loadingDiv.remove();
            
            if (response.credentials && response.credentials.length > 0) {
                // Update count
                countSpan.textContent = `${response.credentials.length} found`;
                
                // Create a grid container for credentials
                const gridContainer = document.createElement("div");
                gridContainer.style.display = "grid";
                gridContainer.style.gridTemplateColumns = "repeat(auto-fill, minmax(250px, 1fr))";
                gridContainer.style.gap = "12px";
                output.appendChild(gridContainer);
                
                response.credentials.forEach((cred) => {
                    const credDiv = document.createElement("div");
                    credDiv.className = "credential-item";
                    
                    // Enhanced styling for credential items to match dropdown
                    Object.assign(credDiv.style, {
                        cursor: "pointer",
                        padding: "0.75rem",
                        border: "1px solid #334155",
                        borderRadius: "0.375rem",
                        backgroundColor: "rgba(15, 23, 42, 0.6)",
                        transition: "all 0.2s ease",
                        display: "flex",
                        flexDirection: "column",
                        gap: "8px",
                        position: "relative",
                        overflow: "hidden"
                    });

                    // Add hover effect to match dropdown
                    credDiv.addEventListener("mouseenter", function() {
                        this.style.backgroundColor = "rgba(15, 23, 42, 0.8)";
                        this.style.borderColor = "#3b82f6";
                    });

                    credDiv.addEventListener("mouseleave", function() {
                        this.style.backgroundColor = "rgba(15, 23, 42, 0.6)";
                        this.style.borderColor = "#334155";
                    });
                    
                    // Create styled credential content
                    const usernameDiv = document.createElement("div");
                    const passwordDiv = document.createElement("div");
                    
                    Object.assign(usernameDiv.style, {
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        fontSize: "0.875rem",
                        color: "#f8fafc"
                    });
                    
                    Object.assign(passwordDiv.style, {
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        fontSize: "0.875rem",
                        color: "#f8fafc"
                    });

                    // Username SVG icon
                    const usernameSvg = `
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" 
                                fill="#94a3b8"/>
                        </svg>
                    `;
                    
                    // Password SVG icon
                    const passwordSvg = `
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 8H17V6C17 3.24 14.76 1 12 1C9.24 1 7 3.24 7 6V8H6C4.9 8 4 8.9 4 10V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V10C20 8.9 19.1 8 18 8ZM12 17C10.9 17 10 16.1 10 15C10 13.9 10.9 13 12 13C13.1 13 14 13.9 14 15C14 16.1 13.1 17 12 17ZM15.1 8H8.9V6C8.9 4.29 10.29 2.9 12 2.9C13.71 2.9 15.1 4.29 15.1 6V8Z" 
                                fill="#94a3b8"/>
                        </svg>
                    `;

                    usernameDiv.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 8px;">
                            ${usernameSvg}
                            <span style="color: #f8fafc;">${cred.username}</span>
                        </div>
                    `;
                    
                    passwordDiv.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 8px;">
                            ${passwordSvg}
                            <span style="color: #f8fafc;">${cred.password}</span>
                        </div>
                    `;
                    
                    credDiv.appendChild(usernameDiv);
                    credDiv.appendChild(passwordDiv);
                    
                    // Add click event listener to autofill credentials
                    credDiv.addEventListener("click", function() {
                        chrome.runtime.sendMessage({
                            action: "autofill",
                            username: cred.username,
                            password: cred.password
                        }, function(response) {
                            if (response.success) {
                                console.log("Autofill successful");
                                window.close(); // Close the popup after successful autofill
                            } else {
                                console.error("Autofill failed:", response.error);
                                alert("Failed to autofill credentials: " + response.error);
                            }
                        });
                    });
                    
                    gridContainer.appendChild(credDiv);
                });
            } else {
                const errorMsg = response.error || "No credentials found.";
                console.error("Error:", errorMsg);
                
                // Update count to show zero
                countSpan.textContent = "0 found";
                
                // Create a nice error message
                const errorDiv = document.createElement("div");
                errorDiv.style.display = "flex";
                errorDiv.style.flexDirection = "column";
                errorDiv.style.alignItems = "center";
                errorDiv.style.justifyContent = "center";
                errorDiv.style.padding = "30px 20px";
                errorDiv.style.color = "#94a3b8";
                errorDiv.style.textAlign = "center";
                
                errorDiv.innerHTML = `
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 15px;">
                        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M15 9L9 15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M9 9L15 15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <div style="font-size: 16px; margin-bottom: 8px;">No credentials found</div>
                    <div style="font-size: 14px; opacity: 0.8;">Try selecting a different website</div>
                `;
                
                output.appendChild(errorDiv);
            }
        });
    });
});