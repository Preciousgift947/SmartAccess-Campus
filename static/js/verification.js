document.addEventListener('DOMContentLoaded', () => {
  const raw = sessionStorage.getItem('verifyResult');
  const content = document.getElementById('verificationContent');
  const invalid = document.getElementById('invalidSection');
  const banner = document.getElementById('verificationBanner');
  const icon = document.getElementById('verificationIcon');
  const title = document.getElementById('verificationTitle');
  const message = document.getElementById('verificationMessage');

  if (!raw) {
    if (content) content.style.display = 'none';
    if (invalid) invalid.style.display = 'block';
    return;
  }

  const { statusCode, data, qrRaw, gate, scannedAt } = JSON.parse(raw);
  const granted = statusCode === 200 && data && data.status === 'Granted';

  const setText = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setText('qrCode', qrRaw || '--');
  setText('scanLocation', gate || 'Main Entrance');
  setText('scanTime', scannedAt || new Date().toLocaleTimeString());

  if (!granted) {
    if (content) content.style.display = 'none';
    if (invalid) {
      invalid.style.display = 'block';
      const p = invalid.querySelector('.invalid-card p');
      if (p) p.textContent =
        (data && data.message) || 'The scanned QR code could not be verified.';
    }
    return;
  }

  // IF GRANTED
  const s = data.student || {};
  const m = data.module || {};
  const initials = `${(s.first_name || '?')[0]}${(s.last_name || '?')[0]}`.toUpperCase();

  if (banner) banner.classList.remove('denied');
  if (icon) icon.textContent = '✓';
  if (title) title.textContent = 'Access Granted';
  if (message) message.textContent = 'Student identity successfully verified.';

  setText('studentPhoto', initials || '--');
  setText('studentName', s.name || 'Unknown Student');
  setText('studentNumber', s.student_number || '--');
  setText('studentEmail', s.email || '--');
  setText('studentCourse', s.course || '--');
  setText('studentFaculty', s.faculty || '--');
  setText('cardExpiry', s.expiry_date || '--');

  const badge = document.getElementById('cardBadge');
  const statusEl = document.getElementById('cardStatus');
  if (badge) {
    badge.textContent = s.card_status || 'Active';
    badge.classList.remove('denied');
    badge.classList.add('active');
  }
  if (statusEl) {
    statusEl.textContent = s.card_status || 'Active';
    statusEl.classList.remove('danger-text');
    statusEl.classList.add('success-text');
  }

  const att = document.getElementById('attendanceStatus');
  if (att) {
    att.textContent = data.attendance || 'Recorded';
    att.classList.remove('danger-text');
    att.classList.add('success-text');
  }

  if (m.code) {
    setText('moduleCode', m.code || '--');
    setText('moduleName', m.name || 'No module loaded');
    setText('moduleVenue', m.venue || '--');
    setText('moduleDay', m.day || '--');
    setText('moduleTime', m.time || '--');
  } else {
    const modSection = document.getElementById('moduleSection');
    if (modSection) modSection.style.display = 'none';
  }

  const confirmBtn = document.getElementById('confirmAccessBtn');
  if (confirmBtn) {
    confirmBtn.textContent = 'Access Confirmed ✓';
    confirmBtn.disabled = true;
  }
});