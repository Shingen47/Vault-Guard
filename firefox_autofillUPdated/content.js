chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "fillFields") {
        console.log("📝 Autofilling fields...");

        let usernameInput = document.querySelector("input[type='email'], input[type='text']");
        let passwordInput = document.querySelector("input[type='password']");

        if (usernameInput && passwordInput) {
            usernameInput.value = request.username;
            passwordInput.value = request.password;
            console.log("✅ Autofilled:", request.username);
        } else {
            console.warn("⚠️ Could not find login fields.");
        }
    }
});
