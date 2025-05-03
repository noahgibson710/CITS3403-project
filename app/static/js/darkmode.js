
// Check if a theme preference is stored in localStorage
window.onload = function() {
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    document.body.classList.add(savedTheme);
} else {
    document.body.classList.add('dark-mode'); // Default theme
}
};

// Function to toggle theme and store preference
function toggleTheme() {
const currentTheme = document.body.classList.contains('light-mode') ? 'light-mode' : 'dark-mode';
const newTheme = currentTheme === 'dark-mode' ? 'light-mode' : 'dark-mode';
document.body.classList.remove(currentTheme);
document.body.classList.add(newTheme);
localStorage.setItem('theme', newTheme); // Save the selected theme
}

