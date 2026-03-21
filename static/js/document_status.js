// // Stop polling on pages where docId is not defined
// if (typeof docId === "undefined" || !docId) {
//     console.log("No docId found — status polling disabled on this page.");
// } else {

//     function updateStatus() {
//         fetch(`/monitoring/api/${docId}/status/`)
//         .then(res => res.json())
//         .then(data => {
//             const statusEl = document.getElementById("status");
//             const spinner = document.getElementById("spinner");

//             statusEl.textContent = data.status;

//             if (data.status === "processing" || data.status === "pending") {
//                 spinner.style.display = "inline-block";
//             } else {
//                 spinner.style.display = "none";
//             }
//         })
//         .catch(err => {
//             console.error("status polling error:", err);
//         });
//     }

//     setInterval(updateStatus, 3000);
//     updateStatus();
// }
