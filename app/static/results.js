// first fetch data
function fetchData() {
    fetch("http://127.0.0.1:5000/")



//then graph it
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