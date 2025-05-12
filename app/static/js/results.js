document.addEventListener("DOMContentLoaded", () => {
  const data = JSON.parse(localStorage.getItem("calcResults"));
  const container = document.getElementById("results-container");
  const saveWrapper = document.getElementById("save-results-wrapper");

  if (data) {
    container.innerHTML = `
      <p><strong>Gender:</strong> ${data.gender.charAt(0).toUpperCase() + data.gender.slice(1)}</p>
      <p><strong>Age:</strong> ${data.age}</p>
      <p><strong>Weight:</strong> ${data.weight} kg</p>
      <p><strong>Height:</strong> ${data.height} cm</p>
      <p><strong>BMR:</strong> ${data.bmr} calories/day</p>
      <p><strong>TDEE:</strong> ${data.tdee} calories/day</p>
      <p><strong>Calorie Goal:</strong> ${capitalizeGoal(data.calorieGoal)}</p> <!-- Add Calorie Goal here -->
      <div style="text-align:center; margin-top: 30px;">
        <a href="/calculator">
          <button style="background-color: #ff6b6b; color: #000; font-weight: bold; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer;">
            Recalculate
          </button>
        </a>
      </div>
      <div id="save-results-wrapper" style="text-align:center; margin-top: 30px;">
        <button id="saveResultsBtn" style="background-color: #4CAF50; color: white; font-weight: bold; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer;">
          Save Results
        </button>
      </div>
    `;

    // Hide the no-results-message if present
    const noResultsMsg = document.querySelector('.no-results-message');
    if (noResultsMsg) {
      noResultsMsg.style.display = 'none';
    }

    // Attach the event listener AFTER the button is in the DOM
    const saveButton = document.getElementById("saveResultsBtn");
    if (saveButton) {
      saveButton.addEventListener("click", () => {
        fetch('/save_results', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            gender: data.gender,
            age: data.age,
            weight: data.weight,
            height: data.height,
            bmr: data.bmr,
            tdee: data.tdee,
            calorie_goal: data.calorieGoal
          })
          
        })
        .then(response => response.json())
        .then(response => {
          if (response.message) {
            // Show a styled popup message
            const popup = document.createElement('div');
            popup.id = 'save-success-popup';
            popup.style.position = 'fixed';
            popup.style.top = '30px';
            popup.style.left = '50%';
            popup.style.transform = 'translateX(-50%)';
            popup.style.background = '#4CAF50';
            popup.style.color = 'white';
            popup.style.padding = '1em 2em';
            popup.style.borderRadius = '10px';
            popup.style.fontSize = '1.2rem';
            popup.style.zIndex = '1000';
            popup.style.boxShadow = '0 2px 10px #0008';
            popup.innerText = 'Results saved successfully!';
            document.body.appendChild(popup);
            setTimeout(() => {
              popup.style.display = 'none';
              localStorage.removeItem("calcResults");
              window.location.href = "/results";
            }, 2500);
          } else {
            alert("Error saving results: " + (response.error || "Unknown error"));
          }
        })
        .catch(error => console.error('Error:', error));
      });
    }
  } else {
    // Hide the save button if there's nothing to save
    if (saveWrapper) saveWrapper.style.display = "none";
  }
});

// Helper function to capitalize the calorie goal
function capitalizeGoal(goal) {
  if (goal === "deficit") {
    return "Calorie Deficit";
  } else if (goal === "surplus") {
    return "Calorie Surplus";
  } else {
    return "Maintenance";
  }
}
