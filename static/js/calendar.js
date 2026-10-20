document.addEventListener("DOMContentLoaded", function () {

    const events = [
        {
            day: 1,
            month: "SEP",
            type: "Assignment",
            title: "Cloud Computing Assignment 1",
            module: "CC101",
            colour: "assignment"
        },
        {
            day: 2,
            month: "SEP",
            type: "Test",
            title: "Internet of Things Test",
            module: "IOT102",
            colour: "test"
        },
        {
            day: 3,
            month: "SEP",
            type: "Assignment",
            title: "Cybersecurity Assignment",
            module: "CYB103",
            colour: "assignment"
        },
        {
            day: 4,
            month: "SEP",
            type: "Examination",
            title: "Software Development Midterm",
            module: "SD104",
            colour: "exam"
        },
        {
            day: 5,
            month: "SEP",
            type: "Assignment",
            title: "Algorithms Assignment",
            module: "ALG105",
            colour: "assignment"
        },
        {
            day: 8,
            month: "SEP",
            type: "Examination",
            title: "Cloud Computing Final",
            module: "CC101",
            colour: "exam"
        },
        {
            day: 9,
            month: "SEP",
            type: "Assignment",
            title: "IoT Assignment",
            module: "IOT102",
            colour: "assignment"
        },
        {
            day: 10,
            month: "SEP",
            type: "Test",
            title: "Cybersecurity Test",
            module: "CYB103",
            colour: "test"
        }
    ];

    const calendar = document.getElementById("calendar");
    const upcoming = document.getElementById("upcomingEvents");

    if (!calendar || !upcoming) {
        return;
    }

    calendar.innerHTML = "";
    upcoming.innerHTML = "";

    for (let day = 1; day <= 30; day++) {

        const cell = document.createElement("div");
        cell.className = "day";

        let html = `
            <div class="number">${day}</div>
        `;

        events.forEach(function (event) {

            if (event.day === day) {

                html += `
                    <div class="event ${event.colour}">
                        <strong>${event.type}</strong>
                        ${event.title}
                    </div>
                `;

            }

        });

        cell.innerHTML = html;
        calendar.appendChild(cell);

    }

    events.forEach(function (event) {

        upcoming.innerHTML += `

            <div class="upcoming-event">

                <div class="event-date">

                    <strong>${String(event.day).padStart(2, "0")}</strong>

                    <span>${event.month}</span>

                </div>

                <div class="event-info">

                    <span class="event-type ${event.colour}-text">

                        ${event.type}

                    </span>

                    <h4>${event.title}</h4>

                    <p>${event.module}</p>

                </div>

            </div>

        `;

    });

    document.getElementById("totalEvents").textContent =
        events.length;

    document.getElementById("assignmentCount").textContent =
        events.filter(e => e.type === "Assignment").length;

    document.getElementById("testCount").textContent =
        events.filter(e => e.type === "Test").length;

    document.getElementById("examCount").textContent =
        events.filter(e => e.type === "Examination").length;

    document.getElementById("previousMonthBtn")
        .addEventListener("click", function () {

            alert("Previous month will be connected to Flask.");

        });

    document.getElementById("nextMonthBtn")
        .addEventListener("click", function () {

            alert("Next month will be connected to Flask.");

        });

    document.getElementById("todayBtn")
        .addEventListener("click", function () {

            alert("Today's date will be highlighted when connected to the backend.");

        });

});