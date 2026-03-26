/* ================================================
   HEROCALL — Platform Shared JS
   Auth, sidebar, mock data, utilities
   ================================================ */

// ---- Mock User ----
const MOCK_USER = {
  id: 'usr_abc123',
  name: 'Sarah Johnson',
  email: 'sarah@brightsmile.com',
  company: 'BrightSmile Dental',
  token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock-jwt-token'
};

// ---- Mock Agents ----
const MOCK_AGENTS = [
  {
    id: 'agt_001',
    name: 'BrightSmile Receptionist',
    status: 'active',
    phone: '(555) 123-4567',
    industry: 'Dental',
    greeting: "Hi, thank you for calling BrightSmile Dental! I'm your AI assistant. How can I help you today?",
    services: ['Cleaning', 'Whitening', 'Crowns', 'Root Canal', 'Emergency'],
    hours: {
      Mon: { open: '08:00', close: '17:00' },
      Tue: { open: '08:00', close: '17:00' },
      Wed: { open: '08:00', close: '17:00' },
      Thu: { open: '08:00', close: '17:00' },
      Fri: { open: '08:00', close: '15:00' },
      Sat: { open: '09:00', close: '13:00' },
      Sun: null
    },
    calendarUrl: 'https://calendly.com/brightsmile',
    callsToday: 12,
    callsThisWeek: 47,
    appointmentsBooked: 18,
    createdAt: '2026-03-10'
  }
];

// ---- Mock Calls ----
const MOCK_CALLS = [
  {
    id: 'call_001', date: '2026-03-25 14:32', caller: 'John Peterson', phone: '(555) 987-6543',
    duration: '3:42', outcome: 'appointment_booked', agentId: 'agt_001',
    summary: 'Caller requested a teeth cleaning appointment. Scheduled for March 28 at 10:00 AM.',
    transcript: [
      { speaker: 'ai', text: "Hi, thank you for calling BrightSmile Dental! I'm your AI assistant. How can I help you today?" },
      { speaker: 'caller', text: "Hi, I'd like to schedule a teeth cleaning please." },
      { speaker: 'ai', text: "Of course! I'd be happy to help you schedule a teeth cleaning. Let me check our available times. Do you have a preferred day?" },
      { speaker: 'caller', text: "Sometime this week if possible, maybe Thursday or Friday?" },
      { speaker: 'ai', text: "I have availability on Thursday March 28th at 10:00 AM or 2:00 PM, and Friday March 29th at 9:00 AM. Which works best for you?" },
      { speaker: 'caller', text: "Thursday at 10 AM sounds perfect." },
      { speaker: 'ai', text: "Excellent! I've booked you for a teeth cleaning on Thursday, March 28th at 10:00 AM. You'll receive a confirmation email shortly. Is there anything else I can help with?" },
      { speaker: 'caller', text: "No, that's all. Thank you!" },
      { speaker: 'ai', text: "You're welcome, John! We look forward to seeing you Thursday. Have a great day!" }
    ]
  },
  {
    id: 'call_002', date: '2026-03-25 11:15', caller: 'Maria Garcia', phone: '(555) 456-7890',
    duration: '2:18', outcome: 'message_taken', agentId: 'agt_001',
    summary: 'Caller asked about insurance acceptance. Left message for front desk to call back with details.',
    transcript: [
      { speaker: 'ai', text: "Hi, thank you for calling BrightSmile Dental! How can I help you today?" },
      { speaker: 'caller', text: "Hi, do you accept Delta Dental insurance?" },
      { speaker: 'ai', text: "That's a great question! We do work with many insurance providers. Let me have our front desk team get back to you with specific details about Delta Dental coverage. Can I get your name and callback number?" },
      { speaker: 'caller', text: "Sure, it's Maria Garcia, 555-456-7890." },
      { speaker: 'ai', text: "Thank you, Maria! Our team will call you back within the hour with all the insurance details. Is there anything else?" },
      { speaker: 'caller', text: "No, thanks!" }
    ]
  },
  {
    id: 'call_003', date: '2026-03-25 09:45', caller: 'Tom Williams', phone: '(555) 321-0987',
    duration: '4:15', outcome: 'appointment_booked', agentId: 'agt_001',
    summary: 'Emergency toothache. Scheduled same-day emergency appointment at 2:00 PM.',
    transcript: [
      { speaker: 'ai', text: "Hi, thank you for calling BrightSmile Dental! How can I help you today?" },
      { speaker: 'caller', text: "I have a really bad toothache, it started last night and it's getting worse." },
      { speaker: 'ai', text: "I'm sorry to hear that! A toothache can be really painful. Let me see if we can get you in for an emergency appointment today. One moment..." },
      { speaker: 'caller', text: "That would be great, I really need to see someone." },
      { speaker: 'ai', text: "Good news — I have an emergency slot available today at 2:00 PM. Would that work for you?" },
      { speaker: 'caller', text: "Yes, absolutely!" },
      { speaker: 'ai', text: "You're booked for today at 2:00 PM. In the meantime, try taking ibuprofen for the pain and avoid very hot or cold foods. See you soon, Tom!" }
    ]
  },
  {
    id: 'call_004', date: '2026-03-24 16:20', caller: 'Linda Chen', phone: '(555) 654-3210',
    duration: '1:55', outcome: 'info_provided', agentId: 'agt_001',
    summary: 'Asked about office hours and location. Provided all details.',
    transcript: [
      { speaker: 'ai', text: "Hi, thank you for calling BrightSmile Dental! How can I help you?" },
      { speaker: 'caller', text: "Hi, what are your office hours?" },
      { speaker: 'ai', text: "We're open Monday through Thursday 8 AM to 5 PM, Friday 8 AM to 3 PM, and Saturday 9 AM to 1 PM. We're closed on Sundays." },
      { speaker: 'caller', text: "Great, and where are you located?" },
      { speaker: 'ai', text: "We're at 456 Oak Avenue, Suite 200, right next to the Whole Foods. There's free parking in our lot." },
      { speaker: 'caller', text: "Perfect, thank you!" }
    ]
  },
  {
    id: 'call_005', date: '2026-03-24 13:08', caller: 'Robert Kim', phone: '(555) 789-0123',
    duration: '5:30', outcome: 'appointment_booked', agentId: 'agt_001',
    summary: 'New patient inquiry. Scheduled initial consultation and cleaning for April 1.',
    transcript: [
      { speaker: 'ai', text: "Hi, thank you for calling BrightSmile Dental! How can I help you today?" },
      { speaker: 'caller', text: "Hi, I'm looking for a new dentist. I just moved to the area." },
      { speaker: 'ai', text: "Welcome to the neighborhood! We'd love to have you as a patient. For new patients, we do an initial consultation that includes X-rays and a cleaning. Would you like to schedule one?" },
      { speaker: 'caller', text: "Yes, that sounds great. What's available?" }
    ]
  },
  {
    id: 'call_006', date: '2026-03-24 10:30', caller: 'Amy Rivera', phone: '(555) 234-5678',
    duration: '2:45', outcome: 'callback_requested', agentId: 'agt_001',
    summary: 'Needs to reschedule existing appointment. Requested callback from front desk.',
    transcript: [
      { speaker: 'ai', text: "Hi, thank you for calling BrightSmile Dental!" },
      { speaker: 'caller', text: "Hi, I need to reschedule my appointment for next Tuesday." },
      { speaker: 'ai', text: "I'd be happy to help with that. Let me have our scheduling team call you back to find a new time that works. What's the best number to reach you?" }
    ]
  },
  {
    id: 'call_007', date: '2026-03-23 15:00', caller: 'David Park', phone: '(555) 876-5432',
    duration: '3:20', outcome: 'appointment_booked', agentId: 'agt_001',
    summary: 'Whitening consultation. Booked for March 30.',
    transcript: []
  },
  {
    id: 'call_008', date: '2026-03-23 11:42', caller: 'Jennifer Adams', phone: '(555) 345-6789',
    duration: '1:30', outcome: 'info_provided', agentId: 'agt_001',
    summary: 'Asked about whitening pricing. Provided general range and suggested consultation.',
    transcript: []
  }
];

// ---- Mock Stats ----
const MOCK_STATS = {
  totalCalls: 156,
  appointmentsBooked: 64,
  avgResponseTime: '1.2s',
  activeAgents: 1
};

// ---- Auth Helpers ----
function isLoggedIn() {
  return !!localStorage.getItem('hc_token');
}

function getUser() {
  const raw = localStorage.getItem('hc_user');
  return raw ? JSON.parse(raw) : null;
}

function setAuth(user) {
  localStorage.setItem('hc_token', user.token);
  localStorage.setItem('hc_user', JSON.stringify(user));
}

function logout() {
  localStorage.removeItem('hc_token');
  localStorage.removeItem('hc_user');
  window.location.href = '/platform/login.html';
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = '/platform/login.html';
    return false;
  }
  return true;
}

// ---- Sidebar Injection ----
function injectSidebar(activePage) {
  const wrapper = document.querySelector('.platform-wrapper');
  if (!wrapper) return;

  const user = getUser() || MOCK_USER;
  const initials = user.name.split(' ').map(n => n[0]).join('');

  const sidebar = document.createElement('aside');
  sidebar.className = 'platform-sidebar';
  sidebar.id = 'platform-sidebar';
  sidebar.innerHTML = `
    <div class="sidebar-section">
      <div class="sidebar-label">Main</div>
      <ul class="sidebar-nav">
        <li><a href="/platform/dashboard.html" class="${activePage === 'dashboard' ? 'active' : ''}"><span class="nav-icon">📊</span> Dashboard</a></li>
        <li><a href="/platform/agent-detail.html" class="${activePage === 'agents' ? 'active' : ''}"><span class="nav-icon">🤖</span> My Agents</a></li>
        <li><a href="/platform/calls.html" class="${activePage === 'calls' ? 'active' : ''}"><span class="nav-icon">📞</span> Call History</a></li>
      </ul>
    </div>
    <div class="sidebar-section">
      <div class="sidebar-label">Settings</div>
      <ul class="sidebar-nav">
        <li><a href="#" class="${activePage === 'settings' ? 'active' : ''}"><span class="nav-icon">⚙️</span> Settings</a></li>
        <li><a href="#" class="${activePage === 'help' ? 'active' : ''}"><span class="nav-icon">❓</span> Help & Support</a></li>
      </ul>
    </div>
    <div class="sidebar-user">
      <div class="sidebar-avatar">${initials}</div>
      <div class="sidebar-user-info">
        <div class="sidebar-user-name">${user.name}</div>
        <div class="sidebar-user-email">${user.email}</div>
      </div>
      <button onclick="logout()" title="Log out" style="background:none;border:none;cursor:pointer;font-size:1rem;color:var(--text-muted);padding:4px;">🚪</button>
    </div>
  `;

  const overlay = document.createElement('div');
  overlay.className = 'sidebar-overlay';
  overlay.id = 'sidebar-overlay';
  overlay.onclick = () => toggleSidebar();

  const toggle = document.createElement('button');
  toggle.className = 'sidebar-toggle';
  toggle.id = 'sidebar-toggle';
  toggle.innerHTML = '☰';
  toggle.onclick = () => toggleSidebar();

  wrapper.prepend(sidebar);
  document.body.appendChild(overlay);
  document.body.appendChild(toggle);
}

function toggleSidebar() {
  const sidebar = document.getElementById('platform-sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  if (sidebar) sidebar.classList.toggle('open');
  if (overlay) overlay.classList.toggle('open');
}

// ---- Utility ----
function formatOutcome(outcome) {
  const map = {
    'appointment_booked': { label: 'Appointment Booked', class: 'badge-green' },
    'message_taken': { label: 'Message Taken', class: 'badge-blue' },
    'info_provided': { label: 'Info Provided', class: 'badge-purple' },
    'callback_requested': { label: 'Callback Requested', class: 'badge-yellow' },
    'voicemail': { label: 'Voicemail', class: 'badge-yellow' },
    'missed': { label: 'Missed', class: 'badge-red' }
  };
  return map[outcome] || { label: outcome, class: 'badge-blue' };
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
}

function formatDateShort(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ---- Export CSV ----
function exportCallsCSV(calls) {
  const headers = ['Date', 'Caller', 'Phone', 'Duration', 'Outcome', 'Summary'];
  const rows = calls.map(c => [
    c.date, c.caller, c.phone, c.duration,
    formatOutcome(c.outcome).label, `"${(c.summary || '').replace(/"/g, '""')}"`
  ]);
  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `herocall-calls-${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
