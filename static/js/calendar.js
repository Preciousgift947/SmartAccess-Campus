document.addEventListener("DOMContentLoaded", async function () {
    const calendar = document.getElementById("calendar");
    const upcoming = document.getElementById("upcomingEvents");

    if (!calendar || !upcoming) {
        return;
    }

    // apiGet sends the user to /login if they are not logged in
    const data = await apiGet("/api/calendar");
    if (!data) {
        return;
    }

    // Convert the API rows into the shape the drawing code uses
    const events = data.events.map(function (e) {
        const date = new Date(e.Event_Date);
        return {
            year: date.getFullYear(),
            monthIndex: date.getMonth(),
            day: date.getDate(),
            month: date.toLocaleString("en", { month: "short" }).toUpperCase(),
            type: e.Event_Type,
            title: e.Event_Description,
            module: e.Module_Code,
            colour: { Assignment: "assignment", Test: "test", Examination: "exam" }[e.Event_Type] || "other"
        };
    });

    events.sort(function (a, b) {
        return new Date(a.year, a.monthIndex, a.day) - new Date(b.year, b.monthIndex, b.day);
    });

    // Start on the month of the first event, so the calendar isn't empty
    const now = new Date();
    let shown = events.length
        ? { year: events[0].year, month: events[0].monthIndex }
        : { year: now.getFullYear(), month: now.getMonth() };

    // Summary counts cover all events
    setText("totalEvents", events.length);
    setText("assignmentCount", events.filter(e => e.type === "Assignment").length);
    setText("testCount", events.filter(e => e.type === "Test").length);
    setText("examCount", events.filter(e => e.type === "Examination").length);

    // Upcoming list shows all events
    upcoming.innerHTML = events.map(function (event) {
        return `
            <div class="upcoming-event">
                <div class="event-date">
                    <strong>${String(event.day).padStart(2, "0")}</strong>
                    <span>${event.month}</span>
                </div>
                <div class="event-info">
                    <span class="event-type ${event.colour}-text">${escapeHtml(event.type)}</span>
                    <h4>${escapeHtml(event.title)}</h4>
                    <p>${escapeHtml(event.module)}</p>
                </div>
            </div>
        `;
    }).join("");

    function renderMonth() {
        const firstDay = new Date(shown.year, shown.month, 1);
        const daysInMonth = new Date(shown.year, shown.month + 1, 0).getDate();

        // Show the month name in the heading, if the page has one with id="monthTitle"
        const title = document.getElementById("monthTitle");
        if (title) {
            title.textContent = firstDay.toLocaleString("en", { month: "long", year: "numeric" });
        }

        // Weeks start on Monday, so offset the first day
        const offset = (firstDay.getDay() + 6) % 7;

        let html = "";
        for (let i = 0; i < offset; i++) {
            html += `<div class="day empty"></div>`;
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const dayEvents = events.filter(e =>
                e.year === shown.year && e.monthIndex === shown.month && e.day === day
            );

            html += `<div class="day"><div class="number">${day}</div>`;
            dayEvents.forEach(function (event) {
                html += `
                    <div class="event ${event.colour}">
                        <strong>${escapeHtml(event.type)}</strong>
                        ${escapeHtml(event.title)}
                    </div>
                `;
            });
            html += `</div>`;
        }

        calendar.innerHTML = html;
    }

    document.getElementById("previousMonthBtn").addEventListener("click", function () {
        shown = shiftMonth(shown, -1);
        renderMonth();
    });

    document.getElementById("nextMonthBtn").addEventListener("click", function () {
        shown = shiftMonth(shown, 1);
        renderMonth();
    });

    document.getElementById("todayBtn").addEventListener("click", function () {
        shown = { year: now.getFullYear(), month: now.getMonth() };
        renderMonth();
    });

    renderMonth();
});

function shiftMonth(current, change) {
    const d = new Date(current.year, current.month + change, 1);
    return { year: d.getFullYear(), month: d.getMonth() };
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = value;
    }
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
}