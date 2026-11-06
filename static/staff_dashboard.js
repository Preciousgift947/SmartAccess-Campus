document.addEventListener("DOMContentLoaded", async function () {
    const body = document.getElementById("recentActivityBody");
    if (!body) {
        return;
    }

    // apiGet sends the user to /login if they are not logged in
    const data = await apiGet("/api/scans");
    if (!data) {
        return;
    }

    const rows = (data.scans || []).slice(0, 5).map(function (s) {
        const time = s.Scan_Time && s.Scan_Time !== "00:00:00"
            ? s.Scan_Time.slice(0, 5)
            : "—";
        const statusClass = s.Status === "Absent" ? "denied" : "granted";

        return `
            <tr>
                <td>
                    <div class="student-cell">
                        <span class="student-avatar">${escapeHtml(initialsOf(s.Student_Name))}</span>
                        <span>${escapeHtml(s.Student_Name)}</span>
                    </div>
                </td>
                <td>${escapeHtml(s.Student_Number)}</td>
                <td>${escapeHtml(s.Gate_Location)}</td>
                <td>${escapeHtml(time)}</td>
                <td><span class="status ${statusClass}">${escapeHtml(s.Status)}</span></td>
            </tr>
        `;
    }).join("");

    body.innerHTML = rows || `<tr><td colspan="5">No verification records yet.</td></tr>`;
});

function initialsOf(name) {
    return String(name || "")
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map(part => part[0].toUpperCase())
        .join("");
}

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
}