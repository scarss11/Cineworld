// Hamburger menu
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

if (hamburger && sidebar) {
  hamburger.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('open');
  });
  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('open');
    });
  }
}

// Modal handlers
function openModal(id) {
  document.getElementById(id)?.classList.add('open');
}
function closeModal(id) {
  document.getElementById(id)?.classList.remove('open');
}
function openEditModal(id, data) {
  const modal = document.getElementById(id);
  if (!modal) return;
  Object.entries(data).forEach(([key, val]) => {
    const el = modal.querySelector(`[name="${key}"]`);
    if (el) el.value = val;
  });
  modal.classList.add('open');
}
// Close on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.classList.remove('open');
  });
});

// Flash auto-dismiss
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => el.remove());
}, 4000);

// Seat selection
const selectedSeats = new Set();
const maxSeats = 8;

document.querySelectorAll('.seat:not(.occupied)').forEach(seat => {
  seat.addEventListener('click', () => {
    const id = seat.dataset.id;
    if (seat.classList.contains('selected')) {
      seat.classList.remove('selected');
      selectedSeats.delete(id);
    } else {
      if (selectedSeats.size >= maxSeats) {
        alert(`Máximo ${maxSeats} asientos por compra`);
        return;
      }
      seat.classList.add('selected');
      selectedSeats.add(id);
    }
    updateSeatSummary();
  });
});

function updateSeatSummary() {
  const countEl = document.getElementById('seatCount');
  const totalEl = document.getElementById('seatTotal');
  const submitBtn = document.getElementById('submitBtn');
  const hiddenInputs = document.getElementById('hiddenInputs');
  const price = parseFloat(document.getElementById('precio')?.dataset?.precio || 0);

  if (countEl) countEl.textContent = selectedSeats.size;
  if (totalEl) totalEl.textContent = `$${(selectedSeats.size * price).toLocaleString('es-CO')}`;
  if (submitBtn) submitBtn.disabled = selectedSeats.size === 0;
  if (hiddenInputs) {
    hiddenInputs.innerHTML = '';
    selectedSeats.forEach(id => {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'asientos[]';
      input.value = id;
      hiddenInputs.appendChild(input);
    });
  }
}

// Logout
document.getElementById('logoutLink')?.addEventListener('click', (e) => {
  e.preventDefault();
  fetch('/logout').then(() => {
    window.location.replace('/login');
  });
});
