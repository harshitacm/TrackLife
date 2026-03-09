// ── File Upload Preview ────────────────────────────────────────────────
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const fileDrop = document.getElementById('fileDrop');

if (fileInput) {
  fileInput.addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
      filePreview.textContent = `📎 Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
      filePreview.classList.remove('hidden');
    }
  });
}

if (fileDrop) {
  fileDrop.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileDrop.style.borderColor = '#3b82f6';
    fileDrop.style.background = '#eff6ff';
  });
  fileDrop.addEventListener('dragleave', () => {
    fileDrop.style.borderColor = '';
    fileDrop.style.background = '';
  });
  fileDrop.addEventListener('drop', (e) => {
    e.preventDefault();
    fileDrop.style.borderColor = '';
    fileDrop.style.background = '';
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      fileInput.dispatchEvent(new Event('change'));
    }
  });
}

// ── Auto-dismiss Flash Messages ────────────────────────────────────────
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity 0.5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  }, 4000);
});

// ── Set today's date as default for date inputs ────────────────────────
const visitDateInput = document.querySelector('input[name="visit_date"]');
if (visitDateInput && !visitDateInput.value) {
  visitDateInput.value = new Date().toISOString().split('T')[0];
}
