/* =============================================
   TYAGI RESORT – main.js
   ============================================= */

document.addEventListener('DOMContentLoaded', function () {

  // ---- AOS init ----
  AOS.init({ duration: 700, once: true, offset: 60 });

  // ---- Navbar scroll effect ----
  const nav = document.getElementById('mainNav');
  function handleScroll () {
    if (window.scrollY > 60) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
    // Back-to-top
    const btt = document.getElementById('backToTop');
    if (btt) {
      if (window.scrollY > 400) btt.classList.add('visible');
      else btt.classList.remove('visible');
    }
  }
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll(); // run once on load

  // ---- Active nav link on scroll ----
  const sections = document.querySelectorAll('section[id]');
  const navLinks  = document.querySelectorAll('.navbar-nav .nav-link');
  const observer  = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(l => l.classList.remove('active'));
        const link = document.querySelector('.navbar-nav .nav-link[href*="#' + entry.target.id + '"]');
        if (link) link.classList.add('active');
      }
    });
  }, { rootMargin: '-40% 0px -55% 0px' });
  sections.forEach(s => observer.observe(s));

  // ---- Animated counters ----
  function animateCounter (el) {
    const target = parseInt(el.getAttribute('data-target'), 10);
    const duration = 1800;
    const step = Math.ceil(target / (duration / 16));
    let current = 0;
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current.toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 16);
  }

  const counterObs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.counter').forEach(c => counterObs.observe(c));

  // ---- Catering form client-side validation ----
  const form = document.getElementById('cateringForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      let isValid = true;
      const required = form.querySelectorAll('[required]');
      required.forEach(field => {
        field.classList.remove('is-invalid');
        if (!field.value.trim()) {
          field.classList.add('is-invalid');
          isValid = false;
        }
      });
      // Email format
      const emailField = form.querySelector('#email');
      if (emailField && emailField.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)) {
        emailField.classList.add('is-invalid');
        isValid = false;
      }
      if (!isValid) {
        e.preventDefault();
        form.querySelector('.is-invalid')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  }

  // ---- Gallery lightbox (simple overlay) ----
  const galleryItems = document.querySelectorAll('.gallery-item');
  let overlay = null;

  galleryItems.forEach(item => {
    item.addEventListener('click', function () {
      const img = this.querySelector('img');
      if (!img) return;

      overlay = document.createElement('div');
      overlay.style.cssText = [
        'position:fixed', 'inset:0', 'background:rgba(0,0,0,0.88)',
        'display:flex', 'align-items:center', 'justify-content:center',
        'z-index:9999', 'cursor:zoom-out', 'padding:20px'
      ].join(';');

      const bigImg = document.createElement('img');
      bigImg.src = img.src.replace('w=800', 'w=1600');
      bigImg.style.cssText = 'max-width:90vw;max-height:88vh;border-radius:0.5rem;box-shadow:0 20px 60px rgba(0,0,0,0.5)';
      bigImg.alt = img.alt;

      overlay.appendChild(bigImg);
      document.body.appendChild(overlay);
      document.body.style.overflow = 'hidden';

      overlay.addEventListener('click', closeOverlay);
      document.addEventListener('keydown', escClose);
    });
  });

  function closeOverlay () {
    if (overlay) { overlay.remove(); overlay = null; document.body.style.overflow = ''; }
    document.removeEventListener('keydown', escClose);
  }
  function escClose (e) { if (e.key === 'Escape') closeOverlay(); }

  // ---- Set min date on event date picker to today ----
  const datePicker = document.getElementById('event_date');
  if (datePicker) {
    const today = new Date().toISOString().split('T')[0];
    datePicker.setAttribute('min', today);
  }

});
