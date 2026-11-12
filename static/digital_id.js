document.addEventListener("DOMContentLoaded", async function () {
    const qrBox = document.getElementById("qr-box");
    if (!qrBox) {
        return;
    }

    try {
        // Real, scannable QR image from the QR endpoint
        const res = await fetch("/api/qr/generate", { credentials: "same-origin" });

        if (res.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data = await res.json();

        if (res.ok && data.qr && data.qr.image) {
            const img = document.createElement("img");
            img.src = data.qr.image;
            img.alt = "Your access QR code";
            qrBox.replaceChildren(img);
        } else {
            qrBox.textContent = data.message || "QR code not available";
        }
    } catch (err) {
        qrBox.textContent = "QR code not available";
    }
});
