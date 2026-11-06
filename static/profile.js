document.addEventListener("DOMContentLoaded", async function () {
  const app = document.getElementById("app");

  // apiGet sends the user to /login if they are not logged in
  const student = await apiGet("/api/student_profile");
  if (!student) return;

  const registered = new Date(student.Registration_Date).toLocaleDateString();

  app.innerHTML = `
    <main class="profile">
      <h1>${escapeHtml(student.First_Name)} ${escapeHtml(student.Last_Name)}</h1>

      <section class="card">
        <h2>Student details</h2>
        <p><strong>Student number:</strong> ${escapeHtml(student.Student_Number)}</p>
        <p><strong>Email:</strong> ${escapeHtml(student.Email)}</p>
        <p><strong>Phone:</strong> ${escapeHtml(student.Phone_Number || "Not provided")}</p>
      </section>

      <section class="card">
        <h2>Academic details</h2>
        <p><strong>Course:</strong> ${escapeHtml(student.Course)}</p>
        <p><strong>Faculty:</strong> ${escapeHtml(student.Faculty)}</p>
        <p><strong>Registered:</strong> ${escapeHtml(registered)}</p>
      </section>
    </main>
  `;
});

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}