/* ===========================
   TRAMPO - JavaScript Principal
   =========================== */

const API = (() => {
  const h = location.hostname;
  return (h === 'localhost' || h === '127.0.0.1' || h === '')
    ? 'http://localhost:5000/api'
    : 'https://trampo-api-pnux.cr.render.com/api';
})();

// ─── AUTH STATE ───────────────────────────────────────────────
const Auth = {
  getToken: () => localStorage.getItem('trampo_token'),
  getUser: () => {
    try { return JSON.parse(localStorage.getItem('trampo_user')); } catch { return null; }
  },
  save: (token, user) => {
    localStorage.setItem('trampo_token', token);
    localStorage.setItem('trampo_user', JSON.stringify(user));
  },
  logout: () => {
    localStorage.removeItem('trampo_token');
    localStorage.removeItem('trampo_user');
    window.location.href = '/frontend/index.html';
  },
  isLoggedIn: () => !!localStorage.getItem('trampo_token'),
  headers: () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('trampo_token')}`
  })
};

// ─── HTTP ─────────────────────────────────────────────────────
async function http(method, path, body = null) {
  const opts = { method, headers: Auth.headers() };
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(API + path, opts);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Erro na requisição');
    return data;
  } catch (err) {
    throw err;
  }
}
const get = (p) => http('GET', p);
const post = (p, b) => http('POST', p, b);
const put = (p, b) => http('PUT', p, b);

// ─── TOAST ────────────────────────────────────────────────────
function toast(msg, type = 'success') {
  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = `toast ${type !== 'success' ? type : ''}`;
  el.innerHTML = `<span>${icons[type]}</span><span>${msg}</span>`;
  container.appendChild(el);
  setTimeout(() => { el.style.animation = 'slideOut 0.3s ease forwards'; setTimeout(() => el.remove(), 300); }, 3500);
}

// ─── MODAL AUTH ───────────────────────────────────────────────
function openAuthModal(tab = 'login') {
  const overlay = document.getElementById('authModal');
  if (!overlay) return;
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
  setAuthTab(tab);
}
function closeAuthModal() {
  const overlay = document.getElementById('authModal');
  if (!overlay) return;
  overlay.classList.remove('active');
  document.body.style.overflow = '';
}
function setAuthTab(tab) {
  document.querySelectorAll('.modal-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  document.getElementById('loginForm').classList.toggle('hidden', tab !== 'login');
  document.getElementById('registerForm').classList.toggle('hidden', tab !== 'register');
}

// ─── LOGIN ────────────────────────────────────────────────────
async function handleLogin(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type=submit]');
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  setLoading(btn, true);
  try {
    const data = await post('/auth/login', { email, password });
    Auth.save(data.token, data.user);
    closeAuthModal();
    updateNavUI();
    toast(`Bem-vindo de volta, ${data.user.name.split(' ')[0]}! 🚀`);
    setTimeout(() => {
      if (data.user.role === 'recruiter') window.location.href = 'pages/recruiter.html';
    }, 500);
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    setLoading(btn, false);
  }
}

// ─── REGISTER ─────────────────────────────────────────────────
async function handleRegister(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type=submit]');
  const name = document.getElementById('regName').value;
  const email = document.getElementById('regEmail').value;
  const password = document.getElementById('regPassword').value;
  const role = document.getElementById('regRole').value;
  if (password.length < 6) { toast('Senha precisa ter 6+ caracteres', 'error'); return; }
  setLoading(btn, true);
  try {
    const data = await post('/auth/register', { name, email, password, role });
    Auth.save(data.token, data.user);
    closeAuthModal();
    updateNavUI();
    toast(`Bem-vindo ao TRAMPO, ${name.split(' ')[0]}! 🎉`);
    setTimeout(() => {
      if (role === 'candidate') window.location.href = 'pages/profile.html';
      else window.location.href = 'pages/recruiter.html';
    }, 800);
  } catch (err) {
    toast(err.message, 'error');
  } finally {
    setLoading(btn, false);
  }
}

// ─── NAV UI ───────────────────────────────────────────────────
function updateNavUI() {
  const user = Auth.getUser();
  const navAuth = document.getElementById('navAuth');
  const navUser = document.getElementById('navUser');
  if (!navAuth || !navUser) return;
  if (user) {
    navAuth.classList.add('hidden');
    navUser.classList.remove('hidden');
    const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    document.getElementById('navAvatar').textContent = initials;
    document.getElementById('navName').textContent = user.name.split(' ')[0];
    if (user.is_premium) {
      const badge = document.getElementById('navBadge');
      if (badge) { badge.textContent = '💎 Premium'; badge.className = 'badge badge-premium'; badge.classList.remove('hidden'); }
    }
  } else {
    navAuth.classList.remove('hidden');
    navUser.classList.add('hidden');
  }
}

// ─── LOADING STATE ────────────────────────────────────────────
function setLoading(btn, loading) {
  if (!btn) return;
  if (loading) {
    btn._text = btn.innerHTML;
    btn.innerHTML = '<div class="spinner"></div> Aguarde...';
    btn.disabled = true;
  } else {
    btn.innerHTML = btn._text || 'Confirmar';
    btn.disabled = false;
  }
}

// ─── SCROLL ANIMATIONS ────────────────────────────────────────
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.1 });
  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
}

// ─── HEADER SCROLL ────────────────────────────────────────────
function initHeaderScroll() {
  const header = document.querySelector('.header');
  if (!header) return;
  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 20);
  });
}

// ─── HAMBURGER MENU ───────────────────────────────────────────
function initHamburger() {
  const ham = document.getElementById('hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (!ham || !navLinks) return;
  ham.addEventListener('click', () => navLinks.classList.toggle('open'));
}

// ─── COUNTER ANIMATION ────────────────────────────────────────
function animateCounter(el, target, duration = 2000) {
  const start = performance.now();
  const update = (time) => {
    const progress = Math.min((time - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(eased * target).toLocaleString('pt-BR');
    if (progress < 1) requestAnimationFrame(update);
    else el.textContent = target.toLocaleString('pt-BR');
  };
  requestAnimationFrame(update);
}
function initCounters() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting && !e.target.dataset.counted) {
        e.target.dataset.counted = true;
        const target = parseInt(e.target.dataset.target);
        animateCounter(e.target, target);
      }
    });
  }, { threshold: 0.5 });
  document.querySelectorAll('[data-target]').forEach(el => observer.observe(el));
}

// ─── DARK MODE ────────────────────────────────────────────────
function initDarkMode() {
  const btn = document.getElementById('darkToggle');
  if (!btn) return;
  const saved = localStorage.getItem('trampo_theme');
  if (saved === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
  btn.addEventListener('click', () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    document.documentElement.setAttribute('data-theme', isDark ? 'light' : 'dark');
    localStorage.setItem('trampo_theme', isDark ? 'light' : 'dark');
    btn.textContent = isDark ? '🌙' : '☀️';
  });
}

// ─── INIT ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateNavUI();
  initScrollAnimations();
  initHeaderScroll();
  initHamburger();
  initCounters();
  initDarkMode();

  // Fecha modal ao clicar fora
  document.getElementById('authModal')?.addEventListener('click', e => {
    if (e.target.id === 'authModal') closeAuthModal();
  });

  // Tabs do modal
  document.querySelectorAll('.modal-tab').forEach(tab => {
    tab.addEventListener('click', () => setAuthTab(tab.dataset.tab));
  });

  // Forms
  document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
  document.getElementById('registerForm')?.addEventListener('submit', handleRegister);
});
