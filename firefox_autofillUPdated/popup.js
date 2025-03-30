document.addEventListener("DOMContentLoaded", function () {
    const siteSelect = document.getElementById("site-select");
    const autofillBtn = document.getElementById("autofill-btn");

    // Fetch credentials from background script
    browser.runtime.sendMessage({ action: "fetchCredentials" }).then((response) => {
        if (response.credentials && response.credentials.length > 0) {
            response.credentials.forEach((cred) => {
                let option = document.createElement("option");
                option.value = cred.website;
                option.textContent = cred.website;
                siteSelect.appendChild(option);
            });
        } else {
            console.error("No credentials received.");
        }
    });

    // Autofill when button is clicked
    autofillBtn.addEventListener("click", () => {
        const selectedSite = siteSelect.value;
        if (selectedSite) {
            browser.runtime.sendMessage({ action: "autofill", website: selectedSite });
        } else {
            alert("Please select a website.");
        }
    });
});
