document.getElementsByName('signup')[0].addEventListener('submit', function (e) {
    e.preventDefault();

    // Collect form data
    const form = this;
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const message = document.getElementById("signup-message");

    // Password validation pattern
    const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$/;
    message.textContent = "";
    message.removeAttribute("class");

    // Client-side password validation
    if (!passwordPattern.test(password)) {
        message.textContent = "❌ Password must be at least 8 characters long and include uppercase, lowercase, and a special character.";
        message.className = "error";
        return;
    }

    // Create FormData for submitting
    const formData = new FormData(form);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/signup", true);

    // Set header for form submission
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    // Prepare form data to send
    let parameters = new URLSearchParams(formData).toString();
    xhttp.send(parameters);

    xhttp.onload = function () {
        if (xhttp.status == 200) {
            document.getElementById("signup-message").textContent = "✅ Signup Successful!";
            message.className = "success";
            // Optional: reset form after successful signup
            form.reset();
        } else {
            try {
                const response = JSON.parse(xhttp.responseText);
                message.textContent = "❌ " + (response["signup-message"] || "Signup Failed!");
            } catch (e) {
                document.getElementById("signup-message").textContent = "❌ Signup Failed!";
            }
            message.className = "error";
        }
    };
});

// Clear message when the user types in any input field
document.querySelectorAll("#signupform input").forEach(input => {
    input.addEventListener("input", function () {
        const message = document.getElementById("signup-message");
        message.textContent = "";
        message.removeAttribute("class");
    });
});

// Password visibility toggle
document.getElementById('show-password-checkbox').addEventListener('change', function () {
    const passwordField = document.getElementById('password');
    passwordField.type = this.checked ? 'text' : 'password';
});