document.addEventListener("DOMContentLoaded", () => {
  const data = JSON.parse(localStorage.getItem("calcResults"));
  const container = document.getElementById("results-container");
  const saveWrapper = document.getElementById("save-results-wrapper");
  const saveButton = document.getElementById("saveResultsBtn");

  if (data) {
    container.innerHTML = `
      <p><strong>Gender:</strong> ${data.gender.charAt(0).toUpperCase() + data.gender.slice(1)}</p>
      <p><strong>Age:</strong> ${data.age}</p>
      <p><strong>Weight:</strong> ${data.weight} kg</p>
      <p><strong>Height:</strong> ${data.height} cm</p>
      <p><strong>BMR:</strong> ${data.bmr} calories/day</p>
      <p><strong>TDEE:</strong> ${data.tdee} calories/day</p>
    `;

    // Only attach the save event if there is data to save
    if (saveButton) {
      saveButton.addEventListener("click", () => {
        fetch('/save_results', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(response => {
          if (response.message) {
            alert(response.message);
            localStorage.removeItem("calcResults");
            window.location.href = "/results"; // Refresh to show updated history
          } else {
            alert("Error saving results: " + (response.error || "Unknown error"));
          }
        })
        .catch(error => console.error('Error:', error));
      });
    }
  } else {
    // Only show the message if there is no macro history on the page
    if (!document.querySelector('.macro-history')) {
      container.innerHTML = "<p style='color:#ff6b6b;'>❌ No results found. Please calculate your macros first on the <a href='/calculator' style='color:#6bffff; text-decoration:underline;'>Macro Calc</a> page.</p>";
    }
    // Hide the save button if there's nothing to save
    if (saveWrapper) saveWrapper.style.display = "none";
  }
  

  // Plot calorie chart (example data)
  Highcharts.chart('calorieChart', {
    chart: {
      type: 'line'
    },
    title: {
      text: 'Daily Calorie Intake'
    },
    xAxis: {
      type: 'datetime',
      title: {
        text: 'Date'
      }
    },
    yAxis: {
      title: {
        text: 'Calories'
      }
    },
    series: [{
      name: 'Calories',
      data: [
        [Date.UTC(2025, 3, 18), 2200],
        [Date.UTC(2025, 3, 19), 2100],
        [Date.UTC(2025, 3, 20), 2300],
        [Date.UTC(2025, 3, 21), 1800],
        [Date.UTC(2025, 3, 22), 2000]
      ]
    }]
  });
});
