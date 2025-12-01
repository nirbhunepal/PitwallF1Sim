function showSection(sectionId) {
    document.querySelectorAll('.page-section').forEach(sec => {
        sec.style.display = 'none';
    });
    document.getElementById(sectionId).style.display = 'block';
}

function loadTelemetry() {
    const driver = document.getElementById('telemetry-driver').value;
    const year = document.getElementById('telemetry-year').value;
    const race = document.getElementById('telemetry-race').value;

    fetch('/get_telemetry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ driver, year, race })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('telemetry-result').innerHTML =
            `<img src="${data.image_path}" style="width:100%; border-radius:10px;">`;
    });
}


function runStrategy() {
    const data = {
        year: document.getElementById("strat-year").value,
        race: document.getElementById("strat-race").value
    };

    fetch("/run_strategy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(res => {
        if (res.status !== "success") {
            document.getElementById("strategy-output").innerHTML =
                `<p style="color:red;">Error: ${res.message}</p>`;
            return;
        }

        let html = `<p><b>Best Strategy:</b> ${res.best_strategy}</p><br>`;

        html += `<table class="strat-table">
                    <tr><th>Strategy</th><th>Predicted Race Time (sec)</th></tr>`;

        for (const [name, time] of Object.entries(res.times)) {
            html += `<tr>
                        <td>${name}</td>
                        <td>${time.toFixed(2)}</td>
                     </tr>`;
        }

        html += `</table>`;

        document.getElementById("strategy-output").innerHTML = html;
    })
    .catch(err => {
        document.getElementById("strategy-output").innerHTML =
            `<p style="color:red;">Server error: ${err}</p>`;
    });
}




