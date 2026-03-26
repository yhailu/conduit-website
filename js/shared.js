/* ================================================
   HEROCALL — Shared Components
   Injects nav, footer, theme toggle into all pages
   ================================================ */

// Use absolute paths for all nav/footer links (clean URLs)
const P = '/';

const LOGO_SVG = `<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="hc-grad" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#059669"/><stop offset="100%" stop-color="#34d399"/></linearGradient></defs><polygon points="36,4 16,34 30,34 26,60 50,26 34,26" fill="url(#hc-grad)"/></svg>`;

// ---- THEME (light only) ----
document.documentElement.setAttribute('data-theme', 'light');

// ---- NAV ----
function injectNav() {
  const el = document.getElementById('site-nav');
  if (!el) return;
  el.outerHTML = `
  <nav class="site-nav" id="site-nav">
   <div class="site-nav-inner">
    <a href="/" class="nav-logo">
      <div class="nav-logo-icon">${LOGO_SVG}</div>
      <span class="nav-logo-text">Hero<span style="color:#10b981">Call</span></span>
    </a>
    <ul class="nav-menu">
      <li class="nav-dropdown"><a href="/solutions">Solutions</a>
        <div class="nav-dropdown-menu">
          <a href="/solutions/ai-lead-capture">AI Lead Capture</a>
          <a href="/solutions/ai-appointment-manager">AI Appointment Manager</a>
          <a href="/solutions/ai-helpdesk">AI Helpdesk</a>
          <a href="/solutions/ai-knowledge-access">AI Knowledge Access</a>
          <a href="/solutions/ai-recruitment">AI Recruitment</a>
          <a href="/solutions/ai-workforce-intelligence">AI Workforce Intelligence</a>
          <a href="/solutions/web-development">Web Development</a>
        </div>
      </li>
      <li class="nav-dropdown"><a href="/industries">Industries</a>
        <div class="nav-dropdown-menu">
          <a href="/industries/healthcare">Healthcare</a>
          <a href="/industries/real-estate">Real Estate</a>
          <a href="/industries/financial-services">Financial Services</a>
          <a href="/industries/saas-digital">SaaS & Digital</a>
          <a href="/industries/education">Education</a>
          <a href="/industries/beauty-wellness">Beauty & Wellness</a>
        </div>
      </li>
      <li><a href="/platform">Platform</a></li>
      <li class="nav-dropdown"><a href="/company/about">Company</a>
        <div class="nav-dropdown-menu">
          <a href="/company/about">About</a>
          <a href="/company/case-studies">Case Studies</a>
          <a href="/faq">FAQ</a>
          <a href="/company/careers">Careers</a>
        </div>
      </li>
      <li><a href="/blog">Blog</a></li>
    </ul>
    <div class="nav-actions">
      <a href="/platform/login" class="btn btn-ghost">Log In</a>
      <a href="/consultation" class="btn btn-primary">Request Consultation</a>
    </div>
    <button class="nav-hamburger" onclick="toggleMobileMenu()" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
   </div>
  </nav>
  <div class="nav-mobile-menu" id="nav-mobile-menu">
    <a href="/solutions" onclick="closeMobileMenu()">Solutions</a>
    <a href="/industries" onclick="closeMobileMenu()">Industries</a>
    <a href="/platform" onclick="closeMobileMenu()">Platform</a>
    <a href="/company/about" onclick="closeMobileMenu()">Company</a>
    <a href="/blog" onclick="closeMobileMenu()">Blog</a>
    <a href="/consultation" class="btn btn-primary mobile-cta" onclick="closeMobileMenu()">Request Consultation</a>
  </div>`;
}

// ---- FOOTER ----
function injectFooter() {
  const el = document.getElementById('site-footer');
  if (!el) return;
  el.outerHTML = `
  <footer class="site-footer" id="site-footer">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="/" class="nav-logo">
          <div class="nav-logo-icon">${LOGO_SVG}</div>
          <span class="nav-logo-text">Hero<span style="color:#10b981">Call</span></span>
        </a>
        <p>Deploy your AI workforce in days. Enterprise-grade automation that actually works.</p>
        <div style="display:flex; gap:12px; margin-top:16px;">
          <a href="https://x.com/herocallio" target="_blank" rel="noopener" aria-label="X/Twitter" style="display:flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:8px; background:var(--bg-card); border:1px solid var(--border); transition:all 0.2s;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="color:var(--text-muted);"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          </a>
          <a href="https://instagram.com/herocall.io" target="_blank" rel="noopener" aria-label="Instagram" style="display:flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:8px; background:var(--bg-card); border:1px solid var(--border); transition:all 0.2s;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="color:var(--text-muted);"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
          </a>
          <a href="https://linkedin.com/company/herocall" target="_blank" rel="noopener" aria-label="LinkedIn" style="display:flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:8px; background:var(--bg-card); border:1px solid var(--border); transition:all 0.2s;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="color:var(--text-muted);"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
          </a>
        </div>
      </div>
      <div class="footer-col">
        <h4>Solutions</h4>
        <a href="/solutions/ai-lead-capture">AI Lead Capture</a>
        <a href="/solutions/ai-appointment-manager">Appointment Manager</a>
        <a href="/solutions/ai-helpdesk">AI Helpdesk</a>
        <a href="/solutions/ai-knowledge-access">Knowledge Access</a>
        <a href="/solutions/ai-recruitment">AI Recruitment</a>
        <a href="/solutions/ai-workforce-intelligence">Workforce Intelligence</a>
        <a href="/solutions/web-development">Web Development</a>
      </div>
      <div class="footer-col">
        <h4>Industries</h4>
        <a href="/industries/healthcare">Healthcare</a>
        <a href="/industries/real-estate">Real Estate</a>
        <a href="/industries/financial-services">Financial Services</a>
        <a href="/industries/saas-digital">SaaS & Digital</a>
        <a href="/industries/education">Education</a>
        <a href="/industries/beauty-wellness">Beauty & Wellness</a>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <a href="/company/about">About</a>
        <a href="/company/careers">Careers</a>
        <a href="/company/case-studies">Case Studies</a>
        <a href="/blog">Blog</a>
        <a href="/faq">FAQ</a>
        <a href="/contact">Contact</a>
        <a href="/consultation">Free Consultation</a>
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
      <span>&copy; ${new Date().getFullYear()} HeroCall. All rights reserved.</span>
      <div class="footer-bottom-links">
        <a href="/privacy">Privacy</a>
        <a href="/terms">Terms</a>
        <a href="/contact">Contact</a>
        <span style="color:var(--border);">|</span>
        <a href="https://x.com/herocallio" target="_blank" rel="noopener">X/Twitter</a>
        <a href="https://instagram.com/herocall.io" target="_blank" rel="noopener">Instagram</a>
        <a href="https://linkedin.com/company/herocall" target="_blank" rel="noopener">LinkedIn</a>
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

// ---- MOBILE MENU ----
function toggleMobileMenu() {
  const menu = document.getElementById('nav-mobile-menu');
  if (menu) menu.classList.toggle('open');
}
function closeMobileMenu() {
  const menu = document.getElementById('nav-mobile-menu');
  if (menu) menu.classList.remove('open');
}

// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {
  injectNav();
  injectFooter();
  initAnimations();
});
