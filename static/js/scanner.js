document.addEventListener("DOMContentLoaded", function () {

    const startCameraBtn =
        document.getElementById("startCameraBtn");

    const stopCameraBtn =
        document.getElementById("stopCameraBtn");

    const cameraPreview =
        document.getElementById("cameraPreview");

    const cameraPlaceholder =
        document.getElementById("cameraPlaceholder");

    const scannerStatus =
        document.getElementById("scannerStatus");

    const scanMessage =
        document.getElementById("scanMessage");

    const messageText =
        document.getElementById("messageText");

    const scanLine =
        document.getElementById("scanLine");

    const qrUpload =
        document.getElementById("qrUpload");


    let cameraStream = null;

    let scanning = false;

    let barcodeDetector = null;


    function updateMessage(message, type = "") {

        messageText.textContent = message;

        scanMessage.classList.remove(
            "success",
            "error"
        );

        if (type) {
            scanMessage.classList.add(type);
        }
    }


    function updateStatus(text, type = "") {

        scannerStatus.textContent = text;

        scannerStatus.classList.remove(
            "scanning",
            "success",
            "error"
        );

        if (type) {
            scannerStatus.classList.add(type);
        }
    }


    async function startCamera() {

        try {

            cameraStream =
                await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: {
                            ideal: "environment"
                        }
                    },
                    audio: false
                });


            cameraPreview.srcObject = cameraStream;

            cameraPreview.style.display = "block";

            cameraPlaceholder.style.display = "none";

            scanLine.classList.add("active");

            startCameraBtn.disabled = true;

            stopCameraBtn.disabled = false;

            scanning = true;


            updateStatus(
                "Scanning",
                "scanning"
            );


            updateMessage(
                "Camera active. Looking for QR code..."
            );


            initialiseQRDetection();

        }

        catch (error) {

            console.error(error);

            updateStatus(
                "Camera Error",
                "error"
            );


            updateMessage(
                "Camera permission was denied or no camera was found.",
                "error"
            );
        }
    }


    function stopCamera() {

        scanning = false;


        if (cameraStream) {

            cameraStream
                .getTracks()
                .forEach(function (track) {

                    track.stop();

                });

            cameraStream = null;
        }


        cameraPreview.srcObject = null;

        cameraPreview.style.display = "none";

        cameraPlaceholder.style.display = "block";

        scanLine.classList.remove("active");

        startCameraBtn.disabled = false;

        stopCameraBtn.disabled = true;


        updateStatus(
            "Ready"
        );


        updateMessage(
            "Waiting for QR code..."
        );
    }


    async function initialiseQRDetection() {

        if (!("BarcodeDetector" in window)) {

            updateMessage(
                "Camera started. Automatic QR detection is not supported by this browser. You can still use the demo scanner.",
                "error"
            );

            return;
        }


        try {

            barcodeDetector =
                new BarcodeDetector({
                    formats: ["qr_code"]
                });


            detectQRCode();

        }

        catch (error) {

            console.error(error);

            updateMessage(
                "QR detection could not be started.",
                "error"
            );
        }
    }


    async function detectQRCode() {

        if (!scanning || !barcodeDetector) {
            return;
        }


        try {

            const codes =
                await barcodeDetector.detect(
                    cameraPreview
                );


            if (codes.length > 0) {

                const qrValue =
                    codes[0].rawValue;


                processQRCode(qrValue);

                return;
            }

        }

        catch (error) {

            console.log(
                "Waiting for readable QR code..."
            );
        }


        requestAnimationFrame(
            detectQRCode
        );
    }

async function submitScannedQR(qrValue) {
    try {
        const gateEl = document.getElementById('gate');
        const res = await fetch('/api/qr/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                qr_data: qrValue,
                gate_location: gateEl ? gateEl.value : 'Main Entrance'
            })
        });

        const data = await res.json();
        showResult(res.status, data);
        return { statusCode: res.status, data };
    } catch (err) {
        console.error(err);
        showResult(0, { message: 'Network error. Please try again.' });
        return { statusCode: 0, data: { message: 'Network error.' } };
    }
}

    function showResult(statusCode, data) {
  const box = document.getElementById('scan-result');
  if (!box) return;

  if (statusCode === 200 && data.status === 'Granted') {
    const s = data.student || {};
    box.className = 'scan-result success';
    box.innerHTML = `
      <h2> Access Granted</h2>
      <p><strong>${s.name || 'Student'}</strong></p>
      <p>${s.student_number || ''} — ${s.course || ''}</p>
      <p class="muted">Attendance: ${data.attendance || 'Recorded'}</p>
    `;
  } else if (statusCode === 401) {
    box.className = 'scan-result warning';
    box.innerHTML = `<h2> ${data.message || 'Unauthorized'}</h2>
      <p>Please log in as staff to scan.</p>`;
  } else {
    box.className = 'scan-result error';
    box.innerHTML = `<h2>Access Denied</h2>
      <p>${data.message || 'Unknown error'}</p>`;
  }
  box.style.display = 'block';
}

async function processQRCode(qrValue) {
    scanning = false;
    scanLine.classList.remove("active");

    updateStatus("Scanning", "scanning");
    updateMessage("Sending QR to server for verification...");

    const gateEl = document.getElementById('gate');
    const gate = gateEl ? gateEl.value : 'Main Entrance';
    const result = await submitScannedQR(qrValue);

    sessionStorage.setItem('verifyResult', JSON.stringify({
        statusCode: result.statusCode,
        data: result.data,
        qrRaw: qrValue,
        gate: gate,
        scannedAt: new Date().toLocaleTimeString()
    }));

    const ok = result.statusCode === 200 && result.data.status === 'Granted';

    updateStatus(ok ? "Verified" : "Denied", ok ? "success" : "error");
    updateMessage(
        ok ? "Access granted. Redirecting..."
           : ((result.data && result.data.message) || "Access denied."),
        ok ? "success" : "error"
    );

    setTimeout(function () {
        window.location.href = "/verification";
    }, 1000);
}


    qrUpload.addEventListener(
        "change",
        async function (event) {

            const file =
                event.target.files[0];


            if (!file) {
                return;
            }


            if (!("BarcodeDetector" in window)) {

                updateMessage(
                    "QR image scanning is not supported by this browser. Use Test QR0001 for now.",
                    "error"
                );

                return;
            }


            try {

                updateStatus(
                    "Reading",
                    "scanning"
                );


                updateMessage(
                    "Reading uploaded QR image..."
                );


                const bitmap =
                    await createImageBitmap(file);


                const detector =
                    new BarcodeDetector({
                        formats: ["qr_code"]
                    });


                const codes =
                    await detector.detect(bitmap);


                if (codes.length === 0) {

                    updateStatus(
                        "Not Found",
                        "error"
                    );


                    updateMessage(
                        "No QR code was detected in the selected image.",
                        "error"
                    );

                    return;
                }


                processQRCode(
                    codes[0].rawValue
                );

            }

            catch (error) {

                console.error(error);


                updateStatus(
                    "Error",
                    "error"
                );


                updateMessage(
                    "The QR image could not be processed.",
                    "error"
                );
            }
        }
    );


    startCameraBtn.addEventListener(
        "click",
        startCamera
    );


    stopCameraBtn.addEventListener(
        "click",
        stopCamera
    );

});