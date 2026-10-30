document.addEventListener("DOMContentLoaded", async function () {
  const app = document.getElementById("app");

  // apiGet sends the user to /login if they are not logged in
  const data = await apiGet("/api/dashboard");
  if (!data) return;

  const card = data.card;
  const cardStatus = card ? card.Card_Status : "No card issued";
  const expiry = card ? new Date(card.Expiry_Date).toLocaleDateString() : "-";

  app.innerHTML = `
    <main class="dashboard">
      <h1>Welcome, ${escapeHtml(data.student_name)}</h1>
      <p class="muted">${escapeHtml(data.course)}</p>

      <section class="card">
        <h2>Digital access card</h2>
        <p>Status: <strong>${escapeHtml(cardStatus)}</strong></p>
        <p>Expires: ${escapeHtml(expiry)}</p>
      </section>

      <section class="card">
        <h2>Notifications</h2>
        <p>${data.unread_notifications} unread</p>
      </section>

      <button id="logout-btn" class="btn primary">Log out</button>
    </main>
  `;

  document.getElementById("logout-btn").addEventListener("click", async function () {
    await apiPost("/api/logout", {});
    window.location.href = "/login";
  });
});

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}