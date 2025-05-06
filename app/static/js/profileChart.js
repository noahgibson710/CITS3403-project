document.addEventListener("DOMContentLoaded", function () {
    const chartContainer = document.getElementById("calorie-chart");

    if (chartContainer && typeof calorieChartData !== "undefined") {
        Highcharts.chart('calorie-chart', {
            chart: {
                type: 'line'
            },
            title: {
                text: 'Calories Over Time'
            },
            xAxis: {
                categories: calorieChartData.dates,
                title: {
                    text: 'Date'
                }
            },
            yAxis: {
                title: {
                    text: 'Calories (cal/day)'
                }
            },
            series: [
                {
                    name: 'TDEE',
                    data: calorieChartData.tdee
                },
                {
                    name: 'BMR',
                    data: calorieChartData.bmr
                }
            ]
        });
    }
});
