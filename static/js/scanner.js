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


    // Decode a QR code from an image or video frame using the jsQR library.
    // Used when the browser has no built-in BarcodeDetector (e.g. Chrome on Windows).
    function decodeWithJsQR(source, width, height, tryInverted) {

        if (typeof jsQR === "undefined" || !width || !height) {
            return null;
        }

        const scale = Math.min(1, 1000 / Math.max(width, height));
        const w = Math.round(width * scale);
        const h = Math.round(height * scale);

        const canvas = document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;

        const ctx = canvas.getContext("2d", { willReadFrequently: true });
        ctx.drawImage(source, 0, 0, w, h);

        const imageData = ctx.getImageData(0, 0, w, h);

        const result = jsQR(imageData.data, w, h, {
            inversionAttempts: tryInverted ? "attemptBoth" : "dontInvert"
        });

        return result ? result.data : null;
    }


    async function initialiseQRDetection() {

        if ("BarcodeDetector" in window) {

            try {

                barcodeDetector =
                    new BarcodeDetector({
                        formats: ["qr_code"]
                    });

            }

            catch (error) {

                console.error(error);

                barcodeDetector = null;
            }
        }


        if (!barcodeDetector && typeof jsQR === "undefined") {

            updateMessage(
                "QR scanning is not available in this browser.",
                "error"
            );

            return;
        }


        detectQRCode();
    }


    async function detectQRCode() {

        if (!scanning) {
            return;
        }


        try {

            let qrValue = null;

            if (barcodeDetector) {

                const codes =
                    await barcodeDetector.detect(
                        cameraPreview
                    );

                if (codes.length > 0) {
                    qrValue = codes[0].rawValue;
                }

            }

            else if (cameraPreview.readyState >= 2) {

                qrValue = decodeWithJsQR(
                    cameraPreview,
                    cameraPreview.videoWidth,
                    cameraPreview.videoHeight,
                    false
                );

            }


            if (qrValue) {

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

  const msg = (data && data.message) || '';
  const isNotLoggedIn = statusCode === 401 && /not\s*logged\s*in/i.test(msg);

  if (statusCode === 200 && data && data.status === 'Granted') {
    const s = data.student || {};
    box.className = 'scan-result success';
    box.innerHTML = `
      <h2>Access Granted</h2>
      <p><strong>${s.name || 'Student'}</strong></p>
      <p>${s.student_number || ''} — ${s.course || ''}</p>
      <p class="muted">Attendance: ${data.attendance || 'Recorded'}</p>
    `;
  } else if (isNotLoggedIn) {
    //when "Not logged in"
    box.className = 'scan-result warning';
    box.innerHTML = `
      <h2>Not logged in</h2>
      <p>Please log in as staff to scan.</p>
    `;
  } else {
    //other errors:
    box.className = 'scan-result error';
    box.innerHTML = `
      <h2>Access Denied</h2>
      <p>${msg || 'Unknown error'}</p>
    `;
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


                let qrValue = null;

                if ("BarcodeDetector" in window) {

                    try {

                        const detector =
                            new BarcodeDetector({
                                formats: ["qr_code"]
                            });

                        const codes =
                            await detector.detect(bitmap);

                        if (codes.length > 0) {
                            qrValue = codes[0].rawValue;
                        }

                    }

                    catch (detectError) {
                        console.log("BarcodeDetector failed, using jsQR");
                    }
                }


                if (!qrValue) {

                    qrValue = decodeWithJsQR(
                        bitmap,
                        bitmap.width,
                        bitmap.height,
                        true
                    );
                }


                if (!qrValue) {

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
                    qrValue
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