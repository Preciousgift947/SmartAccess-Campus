async function apiGet(url) {
  const res = await fetch(url, { credentials: "same-origin" });
  if (res.status === 401) { window.location.href = "/login"; return null; }
  if (!res.ok) throw new Error("Request failed: " + res.status);
  return res.json();
}

async function apiPost(url, body) {
  const res = await fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {})
  });
  return { status: res.status, data: await res.json().catch(() => ({})) };
}
