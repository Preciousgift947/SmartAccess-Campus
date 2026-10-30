document.getElementById("login-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  const identifier = document.getElementById("identifier").value.trim();
  const password = document.getElementById("password").value;

  const result = await apiPost("/api/login", { identifier, password });

  if (result.status === 200 && result.data.success) {
    window.location.href = result.data.role === "admin" ? "/staff-dashboard" : "/dashboard";
  } else {
    alert(result.data.message || "Login failed. Check your details and try again.");
  }
});