    function calculate(event) {
      event.preventDefault(); // Prevent form submission

      const age = parseFloat(document.getElementById('age').value);
      const weight = parseFloat(document.getElementById('weight').value);
      const height = parseFloat(document.getElementById('height').value);
      const gender = document.getElementById('gender').value;
      const activityFactor = parseFloat(document.getElementById('activity').value);

      let bmr;

      if (gender === "male") {
        bmr = (13.397 * weight) + (4.799 * height) - (5.677 * age) + 88.362;
      } else if (gender === "female") {
        bmr = (9.247 * weight) + (3.098 * height) - (4.330 * age) + 447.593;
      }

      const tdee = bmr * activityFactor;

      // Save results to localStorage
      const resultsData = {
        gender,
        age,
        weight,
        height,
        bmr: bmr.toFixed(2),
        tdee: tdee.toFixed(2)
      };
      localStorage.setItem("calcResults", JSON.stringify(resultsData));

      // Show spinner
      document.getElementById("loading-spinner").style.display = "flex";

      // Redirect after short delay
      setTimeout(() => {
        window.location.href = "/results";
      }, 1500);
    }

    window.onload = function () {
      document.querySelector("form").onsubmit = calculate;
    };