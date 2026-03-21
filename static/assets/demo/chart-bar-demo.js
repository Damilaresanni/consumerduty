// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Bar Chart Example
// BAR CHART 1
const ctx1 = document.getElementById('myBarChart').getContext('2d');

new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ['Fees', 'Clarity', 'Misleading Claims'],
        datasets: [{
            label: 'Findings',
            data: [12, 19, 7],
            backgroundColor:'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});


// BAR CHART 2
const ctx2 = document.getElementById('myBarChart2').getContext('2d');

new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: ['Low', 'Medium', 'High'],
        datasets: [{
            label: 'Severity',
            data: [5, 10, 8, 3],
            backgroundColor: [
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(255, 99, 132, 0.6)'
            ],
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});