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
        const signupmessage = document.getElementById("signup-message");
        signupmessage.textContent = "";  
        signupmessage.removeAttribute("class");

        if (xhttp.status == 200) {
            document.getElementById("signup-message").textContent = "✅ Signup Successful!";
            signupmessage.className = "success";
        } else {
            document.getElementById("signup-message").textContent = "❌ Signup Failed!";
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