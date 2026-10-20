const student = {
  name: "Amukelani Maroleni",
  number: "RIC12345",
  course: "Diploma in Information Technology",
  faculty: "Information Technology",
  email: "student@richfield.ac.za",
  status: "Active"
};

const navStudent = [
  ["/dashboard", "⌂", "Dashboard", "dashboard"],
  ["/profile", "◉", "My Profile", "profile"],
  ["/digital_id", "▣", "Digital ID Card", "digital-id"],
  ["/attendance", "✓", "Attendance", "attendance"],
  ["/calendar", "▦", "Academic Calendar", "calendar"],
  ["/notifications", "♢", "Notifications", "notifications"]
];

const navStaff = [
  ["/staff-dashboard", "⌂", "Staff Dashboard", "staff-dashboard"],
  ["/scanner", "▣", "QR Scanner", "scanner"],
  ["/verification", "✓", "Student Verification", "verification"],
  ["/reports", "▤", "Reports", "reports"]
];

function getRole() {
  return localStorage.getItem("smartRole") ||
         document.body.dataset.role ||
         "student";
}

function shell(page, role) {

  const nav = role === "staff" ? navStaff : navStudent;
  const title = role === "staff" ? "Staff Portal" : "Student Portal";

  document.getElementById("app").innerHTML = `
    <div class="app-shell">

      <aside class="sidebar" id="sidebar">

        <div class="logo">
          <div class="logo-badge">SA</div>

          <div>
            <strong>SmartAccess</strong>
            <small>Campus System</small>
          </div>
        </div>

        <div class="nav-title">${title}</div>

        <nav class="nav">

          ${nav.map(n => `
            <a
              class="${page === n[3] ? "active" : ""}"
              href="${n[0]}"
            >
              <span>${n[1]}</span>
              ${n[2]}
            </a>
          `).join("")}

          <a href="/logout">
            <span>↪</span>
            Logout
          </a>

        </nav>

        <div class="sidebar-footer">
          Richfield Graduate Institute of Technology
          <br><br>
          UI/UX Prototype • 2026
        </div>

      </aside>

      <section class="content">

        <header class="topbar">

          <button
            class="menu-toggle"
            onclick="toggleMenu()"
          >
            ☰
          </button>

          <h3>${pageTitle(page)}</h3>

          <div class="user-menu">
            <span>🔔</span>

            <div class="avatar">
              ${role === "staff" ? "ST" : "AM"}
            </div>

            <strong>
              ${role === "staff"
                ? "Security / Staff"
                : student.name}
            </strong>

          </div>

        </header>

        <main class="main">
          ${pageContent(page, role)}
        </main>

      </section>

    </div>
  `;
}

function pageTitle(p) {

  return {
    dashboard: "Student Dashboard",
    profile: "My Profile",
    "digital-id": "Digital Access Card",
    attendance: "Attendance",
    calendar: "Academic Calendar",
    notifications: "Notifications",

    "staff-dashboard": "Staff Dashboard",
    scanner: "QR Scanner",
    verification: "Student Verification",
    reports: "Reports"

  }[p] || "SmartAccess";
}

function pageContent(page, role) {

  /* ==========================================
     STUDENT DASHBOARD
     ========================================== */

  if (page === "dashboard") {
    return `

      <div class="welcome">
        <h1>Welcome back, Amukelani! 👋</h1>
        <p>
          Here is what's happening on your campus account today.
        </p>
      </div>

      <div class="grid stats">

        <div class="stat">
          <div class="icon">👥</div>
          <h2>92%</h2>
          <p>Attendance rate</p>
        </div>

        <div class="stat">
          <div class="icon">▣</div>
          <h2>12</h2>
          <p>Classes attended this month</p>
        </div>

        <div class="stat">
          <div class="icon">🔔</div>
          <h2>3</h2>
          <p>New notifications</p>
        </div>

        <div class="stat">
          <div class="icon">▤</div>
          <h2>2</h2>
          <p>Upcoming assignments</p>
        </div>

      </div>

      <div class="grid two-col">

        <section class="card">

          <div class="card-header">
            <h2>Student Profile</h2>

            <a
              class="btn secondary"
              href="/profile"
            >
              View Profile
            </a>
          </div>

          <div class="profile-head">

            <div class="large-avatar">
              AM
            </div>

            <div>
              <h2>${student.name}</h2>
              <p class="muted">${student.number}</p>
              <p>${student.course}</p>
            </div>

          </div>

          <div class="info-list">

            <div class="info-row">
              <span>Faculty</span>
              <strong>${student.faculty}</strong>
            </div>

            <div class="info-row">
              <span>Status</span>
              <span class="badge success">
                ${student.status}
              </span>
            </div>

          </div>

        </section>


        <section class="card">

          <div class="card-header">
            <h2>Digital Student ID</h2>

            <a
              class="btn secondary"
              href="/digital_id"
            >
              Open
            </a>
          </div>

          <p>
            Use your digital ID and QR code
            for secure campus access.
          </p>

          <div
            class="qr"
            style="width:145px;height:145px;margin:22px auto"
          >
            <span>QR</span>
          </div>

        </section>

      </div>


      <div
        class="grid two-col"
        style="margin-top:18px"
      >

        <section class="card">

          <div class="card-header">
            <h2>Recent Attendance</h2>

            <a href="/attendance">
              View all
            </a>
          </div>

          ${[
            "Web Development",
            "Database Systems",
            "Networking",
            "IT Project Management"
          ].map(x => `
            <div class="info-row">
              <strong>${x}</strong>
              <span class="badge success">
                Present
              </span>
            </div>
          `).join("")}

        </section>


        <section class="card">

          <div class="card-header">
            <h2>Upcoming Classes</h2>

            <a href="/calendar">
              Calendar
            </a>
          </div>

          <div class="info-row">
            <span>08:00 AM</span>
            <strong>
              Web Development — Room IT-12
            </strong>
          </div>

          <div class="info-row">
            <span>10:00 AM</span>
            <strong>
              Database Systems — Room DB-02
            </strong>
          </div>

          <div class="info-row">
            <span>02:00 PM</span>
            <strong>
              Networking — Room NET-05
            </strong>
          </div>

        </section>

      </div>

    `;
  }


  /* ==========================================
     PROFILE
     ========================================== */

  if (page === "profile") {
    return `

      <div class="welcome">
        <h1>My Profile</h1>
        <p>
          View your registered student information.
        </p>
      </div>

      <br>

      <div class="grid profile-layout">

        <section class="card">

          <div class="profile-head">

            <div class="large-avatar">
              AM
            </div>

            <div>
              <h2>${student.name}</h2>

              <p class="muted">
                ${student.number}
              </p>

              <span class="badge success">
                Active
              </span>
            </div>

          </div>


          <div class="info-list">

            <div class="info-row">
              <span>Student Number</span>
              <strong>${student.number}</strong>
            </div>

            <div class="info-row">
              <span>Full Name</span>
              <strong>${student.name}</strong>
            </div>

            <div class="info-row">
              <span>Course</span>
              <strong>${student.course}</strong>
            </div>

            <div class="info-row">
              <span>Faculty</span>
              <strong>${student.faculty}</strong>
            </div>

            <div class="info-row">
              <span>Email</span>
              <strong>${student.email}</strong>
            </div>

            <div class="info-row">
              <span>Status</span>
              <span class="badge success">
                ${student.status}
              </span>
            </div>

          </div>


          <button
            class="btn primary"
            style="margin-top:20px"
            onclick="alert('Edit Profile form would open here.')"
          >
            Edit Profile
          </button>

        </section>


        <section class="card">

          <h2>Quick Access</h2>

          <div class="grid">

            <a
              class="btn secondary"
              href="/digital_id"
            >
              ▣ Digital Access Card
            </a>

            <a
              class="btn secondary"
              href="/attendance"
            >
              ✓ Attendance Records
            </a>

            <a
              class="btn secondary"
              href="/calendar"
            >
              ▦ Academic Calendar
            </a>

          </div>

        </section>

      </div>

    `;
  }


  /* ==========================================
     DIGITAL ID
     ========================================== */

  if (page === "digital-id") {
    return `

      <div class="welcome">
        <h1>Digital Access Card</h1>

        <p>
          Present this QR code for secure
          campus access and verification.
        </p>
      </div>

      <br>

      <div class="card">

        <div class="id-card">

          <div class="id-header">

            <strong>
              RICHFIELD GRADUATE INSTITUTE OF TECHNOLOGY
            </strong>

            <p>
              SMARTACCESS DIGITAL STUDENT ID
            </p>

          </div>


          <div class="id-body">

            <div class="id-person">

              <div class="large-avatar">
                AM
              </div>

              <div>

                <h2>${student.name}</h2>

                <p>${student.number}</p>

                <p>${student.course}</p>

              </div>

            </div>


            <div class="qr">
              <span>SMARTACCESS QR</span>
            </div>


            <p class="id-valid">
              ● Card Active — Valid for Campus Access
            </p>


            <button
              class="btn primary full"
              onclick="window.print()"
            >
              Print / Save ID Card
            </button>

          </div>

        </div>

      </div>

    `;
  }


  /* ==========================================
     ATTENDANCE
     ========================================== */

  if (page === "attendance") {
    return `

      <div class="welcome">
        <h1>Attendance</h1>

        <p>
          Track your attendance history
          and current attendance rate.
        </p>
      </div>

      <br>


      <div class="grid stats">

        <div class="stat">
          <h2>92%</h2>
          <p>Overall attendance</p>
        </div>

        <div class="stat">
          <h2>23</h2>
          <p>Classes attended</p>
        </div>

        <div class="stat">
          <h2>2</h2>
          <p>Classes missed</p>
        </div>

        <div class="stat">
          <h2>25</h2>
          <p>Total classes</p>
        </div>

      </div>


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

              ${[
                "Web Development",
                "Database Systems",
                "Networking",
                "IT Project Management",
                "Software Engineering"
              ].map((x, i) => `
                <tr>

                  <td>${x}</td>

                  <td>
                    10 Jun 2026
                  </td>

                  <td>
                    0${8 + i}:15
                  </td>

                  <td>
                    <span class="badge success">
                      Present
                    </span>
                  </td>

                </tr>
              `).join("")}

            </tbody>

          </table>

        </div>

      </section>

    `;
  }


  /* ==========================================
     ACADEMIC CALENDAR
     ========================================== */

  if (page === "calendar") {
    return `

      <div class="welcome">
        <h1>Academic Calendar</h1>

        <p>
          View classes, tests, assignments
          and examination dates.
        </p>
      </div>

      <br>


      <section class="card">

        <h2>June 2026</h2>

        <div class="calendar-grid">

          ${Array.from(
            { length: 30 },
            (_, i) => `
              <div class="day">

                <small>
                  ${i + 1}
                </small>

                ${
                  [15, 25].includes(i + 1)
                    ? `
                      <span class="event-dot">
                        ${
                          i + 1 === 15
                            ? "Midterm Assessments"
                            : "Guest Lecture"
                        }
                      </span>
                    `
                    : ""
                }

              </div>
            `
          ).join("")}

        </div>

      </section>


      <br>


      <section class="card">

        <h2>Upcoming Academic Events</h2>


        <div class="event">

          <div class="date-box">
            15
            <br>
            <small>JUN</small>
          </div>

          <div>
            <h3>Midterm Assessments</h3>
            <p>15–19 June 2026</p>
          </div>

        </div>


        <div class="event">

          <div class="date-box">
            10
            <br>
            <small>JUL</small>
          </div>

          <div>
            <h3>Project Deadline</h3>
            <p>10 July 2026</p>
          </div>

        </div>

      </section>

    `;
  }


  /* ==========================================
     NOTIFICATIONS
     ========================================== */

  if (page === "notifications") {
    return `

      <div class="welcome">

        <h1>Notifications</h1>

        <p>
          Important academic and campus updates.
        </p>

      </div>

      <br>


      <section class="card">

        <div class="notification">

          <div>🔔</div>

          <div>

            <h3>Assignment Reminder</h3>

            <p>
              Your SmartAccess project assignment
              is due soon.
            </p>

            <small>Today</small>

          </div>

        </div>


        <div class="notification">

          <div>📅</div>

          <div>

            <h3>Upcoming Test</h3>

            <p>
              Check the academic calendar
              for your test schedule.
            </p>

            <small>Yesterday</small>

          </div>

        </div>


        <div class="notification">

          <div>✓</div>

          <div>

            <h3>Attendance Updated</h3>

            <p>
              Your latest attendance record
              has been updated.
            </p>

            <small>2 days ago</small>

          </div>

        </div>

      </section>

    `;
  }


  /* ==========================================
     STAFF DASHBOARD
     ========================================== */

  if (page === "staff-dashboard") {
    return `

      <div class="welcome">

        <h1>Staff Dashboard</h1>

        <p>
          Campus access and student verification
          control centre.
        </p>

      </div>


      <div class="flow">

        <div class="flow-step">
          Staff Login
        </div>

        <span class="arrow">→</span>

        <div class="flow-step">
          QR Scanner
        </div>

        <span class="arrow">→</span>

        <div class="flow-step">
          Verification
        </div>

        <span class="arrow">→</span>

        <div class="flow-step">
          Access / Attendance
        </div>

      </div>


      <div class="grid stats">

        <div class="stat">
          <h2>500</h2>
          <p>Registered students</p>
        </div>

        <div class="stat">
          <h2>420</h2>
          <p>Attendance today</p>
        </div>

        <div class="stat">
          <h2>390</h2>
          <p>QR scans today</p>
        </div>

        <div class="stat">
          <h2>4</h2>
          <p>Pending verifications</p>
        </div>

      </div>


      <div class="grid two-col">

        <section class="card">

          <h2>Quick Actions</h2>

          <div class="grid">

            <a
              class="btn primary"
              href="/scanner"
            >
              Open QR Scanner
            </a>

            <a
              class="btn secondary"
              href="/verification"
            >
              Student Verification
            </a>

            <a
              class="btn secondary"
              href="/reports"
            >
              View Reports
            </a>

          </div>

        </section>


        <section class="card">

          <h2>System Status</h2>

          <div class="info-row">
            <span>Student Registry</span>
            <span class="badge success">
              Connected
            </span>
          </div>

          <div class="info-row">
            <span>QR Verification</span>
            <span class="badge success">
              Online
            </span>
          </div>

        </section>

      </div>

    `;
  }


  /* ==========================================
     QR SCANNER
     ========================================== */

  if (page === "scanner") {
    return `

      <div class="welcome">

        <h1>QR Scanner</h1>

        <p>
          Scan a student's digital access card
          for campus entry.
        </p>

      </div>

      <br>


      <section class="card">

        <div class="scanner-box">

          <div>

            <div class="scan-frame">
              ▣
            </div>

            <h2 style="margin-top:18px">
              Position QR code inside the frame
            </h2>

            <p class="muted">
              Camera access can be connected
              to the QR scanning library later.
            </p>

            <button
              class="btn primary"
              onclick="startScanner()"
            >
              Start Scanner
            </button>

          </div>

        </div>


        <div
          id="scanStatus"
          class="alert"
          style="display:none;margin-top:15px"
        >
        </div>

      </section>

    `;
  }


  /* ==========================================
     VERIFICATION
     ========================================== */

  if (page === "verification") {
    return `

      <div class="welcome">

        <h1>Student Verification</h1>

        <p>
          Verify a scanned student before
          granting campus access.
        </p>

      </div>

      <br>


      <section class="card">

        <div class="verification">

          <div class="verify-avatar">
            AM
          </div>

          <div>

            <h2>${student.name}</h2>

            <p>
              ${student.number} • ${student.course}
            </p>

            <span class="badge success">
              Identity Verified
            </span>

          </div>

        </div>


        <div class="info-list">

          <div class="info-row">
            <span>Access Card</span>
            <strong>Active</strong>
          </div>

          <div class="info-row">
            <span>Student Status</span>
            <strong>Registered</strong>
          </div>

          <div class="info-row">
            <span>Last Scan</span>
            <strong>Today, 08:15</strong>
          </div>

        </div>


        <button
          class="btn primary"
          style="margin-top:20px"
          onclick="alert('Access granted and attendance recorded in the prototype.')"
        >
          Grant Access & Record Attendance
        </button>


        <button
          class="btn danger"
          style="margin-top:20px"
          onclick="alert('Access denied.')"
        >
          Deny Access
        </button>

      </section>

    `;
  }


  /* ==========================================
     REPORTS
     ========================================== */

  if (page === "reports") {
    return `

      <div class="welcome">

        <h1>Reports</h1>

        <p>
          Administrative attendance and campus
          access reporting.
        </p>

      </div>

      <br>


      <section class="card">

        <div class="card-header">

          <h2>Attendance Report</h2>

          <button
            class="btn secondary"
            onclick="window.print()"
          >
            Print Report
          </button>

        </div>


        <div class="grid stats">

          <div class="stat">
            <h2>92%</h2>
            <p>Average attendance</p>
          </div>

          <div class="stat">
            <h2>420</h2>
            <p>Present today</p>
          </div>

          <div class="stat">
            <h2>18</h2>
            <p>Absent today</p>
          </div>

          <div class="stat">
            <h2>390</h2>
            <p>QR scans</p>
          </div>

        </div>


        <div class="table-wrap">

          <table class="table">

            <thead>

              <tr>
                <th>Student</th>
                <th>Student No.</th>
                <th>Last Scan</th>
                <th>Status</th>
              </tr>

            </thead>

            <tbody>

              ${[
                "Amukelani Maroleni",
                "John Smith",
                "Sarah Jones",
                "Thabo Mokoena"
              ].map((n, i) => `
                <tr>

                  <td>${n}</td>

                  <td>
                    RIC12${345 + i}
                  </td>

                  <td>
                    Today, 08:${15 + i}
                  </td>

                  <td>
                    <span class="badge success">
                      Verified
                    </span>
                  </td>

                </tr>
              `).join("")}

            </tbody>

          </table>

        </div>

      </section>

    `;
  }


  /* ==========================================
     DEFAULT
     ========================================== */

  return `

    <section class="card">
      <h2>Page not found</h2>
    </section>

  `;
}


/* ==========================================
   MOBILE MENU
   ========================================== */

function toggleMenu() {

  document
    .getElementById("sidebar")
    .classList
    .toggle("open");

}


/* ==========================================
   LOGOUT
   ========================================== */

function logout() {

  localStorage.removeItem("smartRole");

}


/* ==========================================
   QR SCANNER
   ========================================== */

function startScanner() {

  const el = document.getElementById("scanStatus");

  el.style.display = "block";

  el.textContent =
    "Scanner started in prototype mode. A real camera/QR library can be connected here.";

}


/* ==========================================
   INITIALISE
   ========================================== */

function init() {

  const form = document.getElementById("loginForm");

  if (form) {

    form.addEventListener("submit", e => {

      e.preventDefault();

      localStorage.setItem(
        "smartRole",
        document.getElementById("role").value
      );

      if (
        document.getElementById("role").value === "staff"
      ) {

        location.href = "/staff-dashboard";

      } else {

        location.href = "/dashboard";

      }

    });

    return;
  }


  const page = document.body.dataset.page;

  shell(page, getRole());

}


document.addEventListener(
  "DOMContentLoaded",
  init
);