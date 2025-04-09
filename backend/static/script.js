async function fetchPasswords() {
    try {
        let response = await fetch('/get-passwords');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        let data = await response.json();
        if (Array.isArray(data.passwords)) {
            updatePasswordStats(data.passwords);
        } else {
            console.error('Fetched data is not an array:', data.passwords);
        }
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
}
fetchPasswords();

function checkPasswordStrength(password) {
    let strengthValue = 0;
    if (password.length >= 8) strengthValue += 0.25;
    if (/[A-Z]/.test(password)) strengthValue += 0.25;
    if (/[a-z]/.test(password)) strengthValue += 0.25;
    if (/[0-9]/.test(password)) strengthValue += 0.15;
    if (/[^A-Za-z0-9]/.test(password)) strengthValue += 0.1;

    let strength = 'weak';
    if (strengthValue >= 0.75) strength = 'strong';
    else if (strengthValue >= 0.5) strength = 'medium';

    return { strength, strengthValue };
}

function updatePasswordStats(passwords) {
    const totalPasswords = passwords.length;
    const passwordStrengths = passwords.map(p => checkPasswordStrength(p.password));
    const weakPasswords = passwordStrengths.filter(p => p.strength === 'weak').length;
    const duplicatePasswords = passwords.filter((p, index, self) =>
        index !== self.findIndex(t => t.password === p.password)).length;
    const averageStrength = passwordStrengths.reduce((acc, p) => acc + p.strengthValue, 0) / totalPasswords;

    // Update total passwords
    document.getElementById('total-text').textContent = totalPasswords;
    document.getElementById('total-circle').style.strokeDashoffset = 251.2 - (251.2 * totalPasswords / totalPasswords);
    document.getElementById('total-circle').style.stroke = 'green';

    // Update weak passwords
    document.getElementById('weak-text').textContent = weakPasswords;
    document.getElementById('weak-circle').style.strokeDashoffset = 251.2 - (251.2 * weakPasswords / totalPasswords);
    document.getElementById('weak-circle').style.stroke = 'red';

    // Update duplicate passwords
    document.getElementById('duplicate-text').textContent = duplicatePasswords;
    document.getElementById('duplicate-circle').style.strokeDashoffset = 251.2 - (251.2 * duplicatePasswords / totalPasswords);
    document.getElementById('duplicate-circle').style.stroke = 'orange';

    // Update average strength
    document.getElementById('strength-text').textContent = `${Math.round(averageStrength * 100)}%`;
    document.getElementById('strength-circle').style.strokeDashoffset = 251.2 - (251.2 * averageStrength);
    document.getElementById('strength-circle').style.stroke = averageStrength >= 0.75 ? 'green' : averageStrength >= 0.5 ? 'yellow' : 'red';
}

function scrollToPasswords() {
    document.getElementById('passwords-section').scrollIntoView({ behavior: 'smooth' });
}

async function togglePassword(website, spanId, btn) {
    let passwordSpan = document.getElementById(spanId);
    let icon = btn.querySelector("i");

    // If password is already visible, hide it
    if (passwordSpan.dataset.visible === "true") {
        passwordSpan.textContent = "********";
        passwordSpan.dataset.visible = "false";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
    else {
        // Fetch the actual password from the backend
        let response = await fetch(`/retrieve-password?website=${website}`);
        let data = await response.json();

        if (data.password) {
            passwordSpan.textContent = data.password;
            passwordSpan.dataset.visible = "true";
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");
        }
        else {
            alert("Failed to retrieve password.");
        }
    }
}

function copyPassword(spanId) {
    let passwordText = document.getElementById(spanId).textContent;

    if (passwordText === "********") {
        alert("Please reveal the password before copying.");
        return;
    }

    navigator.clipboard.writeText(passwordText)
        .then(() => {
            alert("Password copied to clipboard!");
        })
        .catch(err => {
            console.error("Failed to copy password: ", err);
        });
}

function searchPassword() {
    let input = document.getElementById('search-bar').value.toLowerCase();
    let tableBody = document.getElementById('password-table-body');
    let rows = tableBody.getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        let website = rows[i].getElementsByTagName('td')[1].textContent.toLowerCase();
        let username = rows[i].getElementsByTagName('td')[2].textContent.toLowerCase();

        if (website.includes(input) || username.includes(input)) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}

function openAddModal() {
    document.getElementById("add-modal").classList.remove("hidden");
}

function closeAddModal() {
    document.getElementById("add-modal").classList.add("hidden");
}

async function submitAddPassword() {
    let website = document.getElementById("add-website").value;
    let username = document.getElementById("add-username").value;
    let password = document.getElementById("add-password").value;

    if (!website || !username || !password) {
        alert("All fields are required!");
        return;
    }

    let response = await fetch("/add-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ website, username, password }),
    });

    let result = await response.json();
    alert(result.message);

    if (response.ok) {
        closeAddModal();
        location.reload();
    }
}

async function submitMasterPassword(website) {
    let password = document.getElementById("master-password").value;

    if (!password) {
        alert("Password Field is required!");
        return;
    }

    let response = await fetch(`/retrieve-password?website=${website}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ method: "password" }),
    });

    let result = await response.json();
    alert(result.message);

    if (response.ok) {
        closeMasterPasswordModal();
        location.reload();
    }
}

function closeMasterPasswordModal() {
    document.getElementById("master-password-modal").classList.add("hidden");
}

// Open and close Edit Modal
function openEditModal(website, username) {
    document.getElementById("edit-modal").classList.remove("hidden");
    document.getElementById("edit-website").value = website;
    document.getElementById("edit-username").value = username;
}

function closeEditModal() {
    document.getElementById("edit-modal").classList.add("hidden");
}

async function submitEditPassword() {
    let website = document.getElementById("edit-website").value;
    let newUsername = document.getElementById("edit-username").value;
    let newPassword = document.getElementById("edit-password").value;

    if (!newUsername || !newPassword) {
        alert("Username and password cannot be empty!");
        return;
    }

    let response = await fetch("/edit-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ website, username: newUsername, password: newPassword }),
    });

    let result = await response.json();
    alert(result.message);

    if (response.ok) {
        closeEditModal();
        location.reload();
    }
}

function openDeleteModal(website) {
    document.getElementById("delete-modal").classList.remove("hidden");
    document.getElementById("delete-website-name").innerText = website;

    document.getElementById("confirm-delete-btn").setAttribute("onclick", `submitDeletePassword('${website}')`);
}

function closeDeleteModal() {
    document.getElementById("delete-modal").classList.add("hidden");
}

async function submitDeletePassword(website) {
    let response = await fetch("/delete-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ website }),
    });

    let result = await response.json();
    alert(result.message);

    if (response.ok) {
        closeDeleteModal();
        location.reload();
    }
}