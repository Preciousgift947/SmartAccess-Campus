document.addEventListener("DOMContentLoaded", async function () {
    const app = document.getElementById("app");
    if (!app) {
        return;
    }

    // apiGet sends the user to /login if they are not logged in
    const data = await apiGet("/api/attendance");
    if (!data) {
        return;
    }

    const records = data.attendance || [];
    const total = records.length;
    const present = records.filter(r => r.Status === "Present").length;
    const late = records.filter(r => r.Status === "Late").length;
    const absent = records.filter(r => r.Status === "Absent").length;
    const attended = present + late;
    const rate = total ? Math.round((attended / total) * 100) : 0;

    const rows = records.map(function (r) {
        const date = new Date(r.Attendance_Date);
        const dateText = isNaN(date) ? "" : date.toLocaleDateString();
        const time = r.Scan_Time && r.Scan_Time !== "00:00:00"
            ? r.Scan_Time.slice(0, 5)
            : "—";
        const badge = r.Status === "Present" ? "badge success" : "badge";

        return `
            <tr>
                <td>${escapeHtml(r.Module_Name)}</td>
                <td>${escapeHtml(dateText)}</td>
                <td>${escapeHtml(time)}</td>
                <td><span class="${badge}">${escapeHtml(r.Status)}</span></td>
            </tr>
        `;
    }).join("");

    app.innerHTML = `
        <div class="welcome">
            <h1>Attendance</h1>
            <p>Track your attendance history and current attendance rate.</p>
        </div>

        <br>

        <div class="grid stats">
            <div class="stat"><h2>${rate}%</h2><p>Attendance rate</p></div>
            <div class="stat"><h2>${attended}</h2><p>Classes attended</p></div>
            <div class="stat"><h2>${absent}</h2><p>Classes missed</p></div>
            <div class="stat"><h2>${total}</h2><p>Total records</p></div>
        </div>

        <br>

        <section class="card">
            <h2>Attendance Records</h2>

            <div class="table-wrap">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Module</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows || `<tr><td colspan="4">No attendance records yet.</td></tr>`}
                    </tbody>
                </table>
            </div>
        </section>
    `;
});

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
}