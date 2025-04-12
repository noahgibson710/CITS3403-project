document.getElementById("loginForm").addEventListener("submit", function (e) {
    e.preventDefault();
  
    const username = this.username.value;
    const password = this.password.value;

    console.log(this)
  
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/login", true);
    xhr.setRequestHeader("Content-Type", "application/json");
  
    xhr.onreadystatechange = function () {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        const msg = document.getElementById("message");
        if (xhr.status === 200) {
          const res = JSON.parse(xhr.responseText);
          msg.innerText = `✅ Logged in as ${res.username}`;
          msg.style.color = "green";
          window.location.href = "/dashboard"; // Optional redirect
        } else {
          msg.innerText = "❌ Invalid username or password";
          msg.style.color = "red";
        }
      }
    };
  
    xhr.send(JSON.stringify({ username, password }));
  });
  