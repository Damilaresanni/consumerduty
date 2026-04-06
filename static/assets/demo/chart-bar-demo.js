// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Bar Chart Example
// BAR CHART 1


const findings = data.findings || [];

// Count by rule
const ruleCounts = {};
// Count by severity
const severityCounts = {
    high: 0,
    medium: 0,
    low: 0
};

findings.forEach(f => {
    // Rule count
    const rule = f.rule_name || "Unknown";
    ruleCounts[rule] = (ruleCounts[rule] || 0) + 1;

    // Severity count
    const s = (f.severity || "").toLowerCase();
    if (severityCounts[s] !== undefined) {
        severityCounts[s]++;
    }
});

const ctx1 = document.getElementById('myBarChart').getContext('2d');

new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: Object.keys(ruleCounts),
        datasets: [{
            label: 'Findings',
            data: Object.values(ruleCounts)
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: false }
        }
    }
});

// BAR CHART 2
const ctx2 = document.getElementById('myBarChart2').getContext('2d');

new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: ['High', 'Medium', 'Low'],
        datasets: [{
            label: 'Severity',
            data: [
                severityCounts.high,
                severityCounts.medium,
                severityCounts.low
            ]
        }]
    },
    options: {
        responsive: true
    }
});