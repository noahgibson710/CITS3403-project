//Send form data to server via POST method
document.getElementById('signupform').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/signup", true);

    let parameters = new URLSearchParams(formData).toString();
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded"); //HTTP request header
    xhttp.send(parameters);

    xhttp.onload = function () {
        const password = document.getElementById('password').value;
        const message = document.getElementById("signup-message");
        const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$/; // A password needs to have at least: one lowercase + one uppercase + one special character + 8 characters long
        const signupmessage = document.getElementById("signup-message");
        signupmessage.textContent = "";  
        signupmessage.removeAttribute("class");

        if (!passwordPattern.test(password)) {       //Password validation
            message.textContent = "❌ Password must be at least 8 characters long and include uppercase, lowercase, and a special character.";
            message.className = "error";
            return;
        }

        if (xhttp.status == 200) {
            document.getElementById("signup-message").textContent = "✅ Signup Successful!";
            signupmessage.className = "success";
        } else {
            try {
                const response = JSON.parse(xhttp.responseText);
                signupmessage.textContent = "❌ " + (response["signup-message"] || "Signup Failed!");
            } catch (e) {
                document.getElementById("signup-message").textContent = "❌ Signup Failed!";
            }
            signupmessage.className = "error";
        }
    };
});

// When the input changes, remove signup-message
document.querySelectorAll("#signupform input").forEach(input => {
    input.addEventListener("input", function () {
      const message = document.getElementById("signup-message");
      message.textContent = "";
      message.removeAttribute("class");
    });
  });

  // Users can make their passwords visible when signing up so that they can check whether the password meets the requirement 
document.getElementById('show-password-checkbox').addEventListener('change', function () {
    const passwordField = document.getElementById('password');
    passwordField.type = this.checked ? 'text' : 'password';
});
