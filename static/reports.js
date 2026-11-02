document.addEventListener("DOMContentLoaded", async function () {
    // apiGet sends the user to /login if they are not logged in
    const data = await apiGet("/api/scans");
    if (!data) {
        return;
    }

    const scans = data.scans || [];
    const total = scans.length;
    const present = scans.filter(s => s.Status === "Present").length;
    const late = scans.filter(s => s.Status === "Late").length;
    const attended = present + late;
    const successRate = total ? Math.round((attended / total) * 100) : 0;
    const lateRate = total ? Math.round((late / total) * 100) : 0;

    // Count scans per location, ignoring absent students with no scan
    const locations = {};
    scans
        .filter(s => s.Gate_Location && s.Gate_Location !== "No Scan")
        .forEach(s => {
            locations[s.Gate_Location] = (locations[s.Gate_Location] || 0) + 1;
        });
    const locationNames = Object.keys(locations);
    const busiest = locationNames.sort((a, b) => locations[b] - locations[a])[0] || "—";

    setText("totalScans", total);
    setText("grantedCount", present);
    setText("lateCount", late);
    setText("activeLocations", locationNames.length);
    setText("successRate", successRate + "%");
    setText("lateRate", lateRate + "%");
    setText("busiestLocation", busiest);

    const rows = scans.slice(0, 20).map(function (s) {
        const date = new Date(s.Attendance_Date);
        const dateText = isNaN(date)
            ? ""
            : date.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
        const time = s.Scan_Time && s.Scan_Time !== "00:00:00"
            ? s.Scan_Time.slice(0, 5)
            : "—";
        const statusClass = s.Status === "Absent" ? "denied" : "granted";

        return `
            <tr>
                <td>${escapeHtml(s.Student_Name)}</td>
                <td>${escapeHtml(s.Student_Number)}</td>
                <td>${escapeHtml(s.Gate_Location)}</td>
                <td>${escapeHtml(dateText)}</td>
                <td>${escapeHtml(time)}</td>
                <td>
                    <span class="report-status ${statusClass}">
                        ${escapeHtml(s.Status)}
                    </span>
                </td>
            </tr>
        `;
    }).join("");

    const body = document.getElementById("activityBody");
    if (body) {
        body.innerHTML = rows || `<tr><td colspan="6">No scans recorded yet.</td></tr>`;
    }
});

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = value;
    }
}

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
}