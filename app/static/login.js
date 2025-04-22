document.getElementById('loginForm').addEventListener('submit', function (e) {
  e.preventDefault(); // stop page reload

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert('Login successful!');
      window.location.href = '/dashboard';
    } else {
      alert('Login failed!');
    }
  });
});
