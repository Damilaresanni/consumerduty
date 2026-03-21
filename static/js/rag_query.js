document.getElementById("ask-btn").addEventListener("click", () => {
    const query = document.getElementById("query-input").value;
    const spinner = document.getElementById("spinner");
    const resultsDiv = document.getElementById("results");

    spinner.style.display = "inline-block";
    resultsDiv.innerHTML = "";

    fetch(`monitoring/api/products/${productId}/rag/`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query})
    })
    .then(res => res.json())
    .then(data => {
        spinner.style.display = "none";

        if (data.error) {
            resultsDiv.innerHTML = `<p class="text-danger">${data.error}</p>`;
            return;
        }

        resultsDiv.innerHTML = data.results.map(r => `
            <div class="card mb-3">
                <div class="card-body">
                    <p>${r.text}</p>
                    <small class="text-muted">Score: ${r.score.toFixed(4)}</small>
                </div>
            </div>
        `).join("");
    })
    .catch(err => {
        spinner.style.display = "none";
        resultsDiv.innerHTML = `<p class="text-danger">Error: ${err}</p>`;
    });
});

function renderFindings(findings) {
    const table = document.getElementById("findingsTable");
    table.innerHTML = "";

    findings.forEach(f => {
        const row = `
            <tr>
                <td>${f.rule}</td>
                <td>${f.fca_ref}</td>
                <td>
                    <span class="badge 
                        ${f.severity === "High" ? "bg-danger" : 
                          f.severity === "Medium" ? "bg-warning text-dark" : 
                          "bg-success"}">
                        ${f.severity}
                    </span>
                </td>
                <td>${f.snippet}</td>
            </tr>
        `;
        table.innerHTML += row;
    });
}
