/* ================================================
   ORCHESTRAFLOW — Shared Components
   Injects nav, footer, theme toggle into all pages
   ================================================ */

// Detect path depth for relative links
const depth = (function() {
  const path = window.location.pathname;
  const parts = path.split('/').filter(p => p && !p.endsWith('.html'));
  // Check if we're in a subdirectory
  if (path.includes('/solutions/') || path.includes('/industries/') || path.includes('/platform/') || path.includes('/company/') || path.includes('/blog/')) {
    return '../';
  }
  return './';
})();

const P = depth; // short alias

const LOGO_SVG = `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <line x1="4" y1="10" x2="28" y2="30" stroke="#3b82f6" stroke-width="1.5" opacity="0.3" stroke-linecap="round"/>
  <line x1="4" y1="24" x2="28" y2="31" stroke="#3b82f6" stroke-width="1.5" opacity="0.4" stroke-linecap="round"/>
  <line x1="4" y1="40" x2="28" y2="33" stroke="#3b82f6" stroke-width="1.5" opacity="0.4" stroke-linecap="round"/>
  <line x1="4" y1="54" x2="28" y2="34" stroke="#3b82f6" stroke-width="1.5" opacity="0.3" stroke-linecap="round"/>
  <circle cx="32" cy="32" r="4" fill="#3b82f6"/>
  <circle cx="32" cy="32" r="7" fill="#3b82f6" opacity="0.1"/>
  <line x1="36" y1="30" x2="60" y2="10" stroke="#3b82f6" stroke-width="1.5" opacity="0.3" stroke-linecap="round"/>
  <line x1="36" y1="31" x2="60" y2="24" stroke="#3b82f6" stroke-width="1.5" opacity="0.4" stroke-linecap="round"/>
  <line x1="36" y1="33" x2="60" y2="40" stroke="#3b82f6" stroke-width="1.5" opacity="0.4" stroke-linecap="round"/>
  <line x1="36" y1="34" x2="60" y2="54" stroke="#3b82f6" stroke-width="1.5" opacity="0.3" stroke-linecap="round"/>
  <circle cx="60" cy="10" r="2" fill="#3b82f6" opacity="0.4"/>
  <circle cx="60" cy="24" r="2" fill="#3b82f6" opacity="0.5"/>
  <circle cx="60" cy="40" r="2" fill="#3b82f6" opacity="0.5"/>
  <circle cx="60" cy="54" r="2" fill="#3b82f6" opacity="0.4"/>
</svg>`;

// ---- THEME (light only) ----
document.documentElement.setAttribute('data-theme', 'light');

// ---- NAV ----
function injectNav() {
  const el = document.getElementById('site-nav');
  if (!el) return;
  el.outerHTML = `
  <nav class="site-nav" id="site-nav">
    <a href="${P}index.html" class="nav-logo">
      <div class="nav-logo-icon">${LOGO_SVG}</div>
      <span class="nav-logo-text">orchestraflow</span>
    </a>
    <ul class="nav-menu">
      <li class="nav-dropdown"><a href="${P}solutions/index.html">Solutions</a>
        <div class="nav-dropdown-menu">
          <a href="${P}solutions/ai-lead-capture.html">AI Lead Capture</a>
          <a href="${P}solutions/ai-appointment-manager.html">AI Appointment Manager</a>
          <a href="${P}solutions/ai-helpdesk.html">AI Helpdesk</a>
          <a href="${P}solutions/ai-knowledge-access.html">AI Knowledge Access</a>
          <a href="${P}solutions/ai-recruitment.html">AI Recruitment</a>
          <a href="${P}solutions/ai-workforce-intelligence.html">AI Workforce Intelligence</a>
        </div>
      </li>
      <li class="nav-dropdown"><a href="${P}industries/index.html">Industries</a>
        <div class="nav-dropdown-menu">
          <a href="${P}industries/healthcare.html">Healthcare</a>
          <a href="${P}industries/real-estate.html">Real Estate</a>
          <a href="${P}industries/financial-services.html">Financial Services</a>
          <a href="${P}industries/saas-digital.html">SaaS & Digital</a>
          <a href="${P}industries/education.html">Education</a>
          <a href="${P}industries/beauty-wellness.html">Beauty & Wellness</a>
        </div>
      </li>
      <li><a href="${P}platform/index.html">Platform</a></li>
      <li><a href="${P}company/about.html">Company</a></li>
      <li><a href="${P}blog/index.html">Blog</a></li>
    </ul>
    <div class="nav-actions">
      <a href="${P}consultation.html" class="btn btn-primary">Request Consultation</a>
    </div>
  </nav>`;
}

// ---- FOOTER ----
function injectFooter() {
  const el = document.getElementById('site-footer');
  if (!el) return;
  el.outerHTML = `
  <footer class="site-footer" id="site-footer">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="${P}index.html" class="nav-logo">
          <div class="nav-logo-icon">${LOGO_SVG}</div>
          <span class="nav-logo-text">orchestraflow</span>
        </a>
        <p>Deploy your AI workforce in days. Enterprise-grade automation that actually works.</p>
      </div>
      <div class="footer-col">
        <h4>Solutions</h4>
        <a href="${P}solutions/ai-lead-capture.html">AI Lead Capture</a>
        <a href="${P}solutions/ai-appointment-manager.html">Appointment Manager</a>
        <a href="${P}solutions/ai-helpdesk.html">AI Helpdesk</a>
        <a href="${P}solutions/ai-knowledge-access.html">Knowledge Access</a>
        <a href="${P}solutions/ai-recruitment.html">AI Recruitment</a>
        <a href="${P}solutions/ai-workforce-intelligence.html">Workforce Intelligence</a>
      </div>
      <div class="footer-col">
        <h4>Industries</h4>
        <a href="${P}industries/healthcare.html">Healthcare</a>
        <a href="${P}industries/real-estate.html">Real Estate</a>
        <a href="${P}industries/financial-services.html">Financial Services</a>
        <a href="${P}industries/saas-digital.html">SaaS & Digital</a>
        <a href="${P}industries/education.html">Education</a>
        <a href="${P}industries/beauty-wellness.html">Beauty & Wellness</a>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <a href="${P}company/about.html">About</a>
        <a href="${P}company/careers.html">Careers</a>
        <a href="${P}platform/index.html">Platform</a>
        <a href="${P}blog/index.html">Blog</a>
        <a href="${P}consultation.html">Free Consultation</a>
      </div>
    </div>
    <div class="footer-newsletter">
      <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap; justify-content:space-between; max-width:1200px; margin:0 auto 24px; padding-bottom:24px; border-bottom:1px solid var(--border);">
        <div>
          <h4 style="font-size:0.9rem; font-weight:700; margin-bottom:2px;">Subscribe to our newsletter</h4>
          <p style="font-size:0.8rem; color:var(--text-muted);">Weekly AI insights. No spam.</p>
        </div>
        <form class="newsletter-form" style="margin:0;" onsubmit="handleNewsletter(event)">
          <div class="newsletter-input-wrap" style="padding:4px 4px 4px 12px;">
            <input type="email" placeholder="your@email.com" required style="font-size:0.85rem;">
            <button type="submit" class="btn btn-primary" style="padding:8px 16px; font-size:0.8rem;">Subscribe</button>
          </div>
        </form>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; ${new Date().getFullYear()} OrchestraFlow. All rights reserved.</span>
      <div class="footer-bottom-links">
        <a href="#">Privacy</a>
        <a href="#">Terms</a>
        <a href="#">Cookies</a>
      </div>
    </div>
  </footer>`;
}

// ---- FADE-IN ANIMATIONS ----
function initAnimations() {
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.1 });
  document.querySelectorAll('.fade-in').forEach(el => obs.observe(el));
}

// ---- Newsletter signup handler ----
async function handleNewsletter(e) {
  e.preventDefault();
  const form = e.target;
  const emailInput = form.querySelector('input[type="email"]');
  const btn = form.querySelector('button');
  const email = emailInput.value.trim();

  if (!email) return;

  const origText = btn.textContent;
  btn.textContent = 'Subscribing...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/newsletter/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, source: window.location.pathname })
    });
    const data = await res.json();

    const success = document.getElementById('newsletter-success');
    if (success) {
      form.style.display = 'none';
      success.style.display = 'block';
    } else {
      emailInput.value = '';
      btn.textContent = '✓ Subscribed!';
      setTimeout(() => { btn.textContent = origText; btn.disabled = false; }, 3000);
      return;
    }
  } catch (err) {
    // Fallback to localStorage if API is unavailable
    const subscribers = JSON.parse(localStorage.getItem('of_subscribers') || '[]');
    if (!subscribers.includes(email)) {
      subscribers.push(email);
      localStorage.setItem('of_subscribers', JSON.stringify(subscribers));
    }
    const success = document.getElementById('newsletter-success');
    if (success) {
      form.style.display = 'none';
      success.style.display = 'block';
    } else {
      emailInput.value = '';
      btn.textContent = '✓ Subscribed!';
      setTimeout(() => { btn.textContent = origText; btn.disabled = false; }, 3000);
    }
  }

  btn.textContent = origText;
  btn.disabled = false;
}

// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {
  injectNav();
  injectFooter();
  initAnimations();
});
