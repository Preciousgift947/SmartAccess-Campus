document.addEventListener("DOMContentLoaded", async function () {
    const list = document.getElementById("notificationList");
    if (!list) {
        return;
    }

    // apiGet sends the user to /login if they are not logged in.
    // The API marks notifications as read when it is called, but it
    // returns their state from before that update, so this visit still
    // highlights the unread ones.
    const data = await apiGet("/api/notifications");
    if (!data) {
        return;
    }

    const items = data.notifications || [];
    const academic = items.filter(n => n.Event_Type);
    const system = items.filter(n => !n.Event_Type);
    const unread = items.filter(n => !n.Is_Read);

    setText("totalCount", items.length);
    setText("academicCount", academic.length);
    setText("systemCount", system.length);
    setText("unreadCount", unread.length);
    setText("academicTypeCount", academic.length);
    setText("systemTypeCount", system.length);

    list.innerHTML = items.length
        ? items.map(renderItem).join("")
        : `<p>No notifications yet.</p>`;
});

function renderItem(n) {
    const isAcademic = Boolean(n.Event_Type);
    const unreadClass = n.Is_Read ? "" : " unread";

    const sent = new Date(n.Sent_Date);
    const sentText = isNaN(sent)
        ? ""
        : sent.toLocaleString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });

    const eventDate = n.Event_Date ? new Date(n.Event_Date) : null;
    const eventText = eventDate && !isNaN(eventDate)
        ? `Event date: ${eventDate.toLocaleDateString("en-GB", { day: "2-digit", month: "long", year: "numeric" })}`
        : "";

    return `
        <div class="notification-entry${unreadClass}">
            <div class="notification-icon ${isAcademic ? "academic" : "info"}">
                ${isAcademic ? "31" : "i"}
            </div>
            <div class="notification-content">
                <div class="notification-top">
                    <div>
                        <span class="notification-type">
                            ${isAcademic ? "Academic Reminder" : "System Update"}
                        </span>
                        <h4>${escapeHtml(n.Message)}</h4>
                    </div>
                    <span class="notification-date">${escapeHtml(sentText)}</span>
                </div>
                <p>${escapeHtml(eventText)}</p>
            </div>
        </div>
    `;
}

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