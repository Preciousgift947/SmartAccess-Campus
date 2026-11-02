document.addEventListener("DOMContentLoaded", async function () {
    const app = document.getElementById("app");
    if (!app) {
        return;
    }

    // apiGet sends the user to /login if they are not logged in
    const student = await apiGet("/api/digital_id");

    if (!student || !student.Student_ID) {
        app.innerHTML = `
            <div class="welcome">
                <h1>Digital Access Card</h1>
                <p>No digital ID card has been issued yet.</p>
            </div>
        `;
        return;
    }

    const fullName = `${student.First_Name} ${student.Last_Name}`;
    const status = student.Card_Status || "Unknown";
    const expiry = new Date(student.Expiry_Date);
    const expiryText = isNaN(expiry) ? "Not available" : expiry.toLocaleDateString();
    const validText = status === "Active"
        ? "● Card Active — Valid for Campus Access"
        : "● Card is not active";

    app.innerHTML = `
        <div class="welcome">
            <h1>Digital Access Card</h1>
            <p>Present this QR code for secure campus access and verification.</p>
        </div>

        <br>

        <div class="card">
            <div class="id-card">
                <div class="id-header">
                    <strong>RICHFIELD GRADUATE INSTITUTE OF TECHNOLOGY</strong>
                    <p>SMARTACCESS DIGITAL STUDENT ID</p>
                </div>

                <div class="id-body">
                    <div class="id-person">
                        <div>
                            <h2>${escapeHtml(fullName)}</h2>
                            <p>${escapeHtml(student.Student_Number)}</p>
                            <p>${escapeHtml(student.Course)}</p>
                        </div>
                    </div>

                    <div class="qr">
                        <span>${escapeHtml(student.QR_Code_Data)}</span>
                    </div>

                    <p>Status: <strong>${escapeHtml(status)}</strong></p>
                    <p>Expires: ${escapeHtml(expiryText)}</p>
                    <p class="id-valid">${validText}</p>

                    <button class="btn primary full" onclick="window.print()">
                        Print / Save ID Card
                    </button>
                </div>
            </div>
        </div>
    `;
});

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
}