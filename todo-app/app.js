/* ─────────────────────────────────────────────────────────────
   TaskFlow — app.js
   Vanilla JS | localStorage as db.json | No dependencies
   ───────────────────────────────────────────────────────────── */

// ══════════════════════════════════════════════════════════════
//  DB — localStorage simulating a db.json
//  Shape: { users: [...], todos: [...] }
// ══════════════════════════════════════════════════════════════

const DB_KEY           = 'taskflow_db';
const CURRENT_USER_KEY = 'currentUser';

function loadDB() {
  const raw = localStorage.getItem(DB_KEY);
  if (raw) {
    try { return JSON.parse(raw); } catch {}
  }
  const initial = { users: [], todos: [] };
  saveDB(initial);
  return initial;
}

function saveDB(db) {
  localStorage.setItem(DB_KEY, JSON.stringify(db));
}

// ══════════════════════════════════════════════════════════════
//  CURRENT USER helpers
// ══════════════════════════════════════════════════════════════

function getCurrentUser() {
  const raw = localStorage.getItem(CURRENT_USER_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

function setCurrentUser(user) {
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
}

function clearCurrentUser() {
  localStorage.removeItem(CURRENT_USER_KEY);
}

// ══════════════════════════════════════════════════════════════
//  SCREEN ROUTING
// ══════════════════════════════════════════════════════════════

const SCREENS = {
  login:     document.getElementById('screen-login'),
  register:  document.getElementById('screen-register'),
  dashboard: document.getElementById('screen-dashboard'),
};

function showScreen(name) {
  Object.values(SCREENS).forEach(s => {
    s.classList.add('hidden');
    s.classList.remove('fade-in');
  });
  const target = SCREENS[name];
  target.classList.remove('hidden');
  // Trigger reflow so animation restarts
  void target.offsetWidth;
  target.classList.add('fade-in');
}

// ══════════════════════════════════════════════════════════════
//  VALIDATION HELPERS
// ══════════════════════════════════════════════════════════════

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showFieldError(errElId, msg) {
  const el = document.getElementById(errElId);
  if (!el) return;
  const msgSpan = document.getElementById(errElId + '-msg');
  if (msgSpan) msgSpan.textContent = msg;
  else el.textContent = msg;
  el.classList.remove('hidden');
  el.classList.add('slide-down');
}

function hideFieldError(errElId) {
  const el = document.getElementById(errElId);
  if (el) el.classList.add('hidden');
}

function showGlobalError(errElId, msg) {
  const el = document.getElementById(errElId);
  if (!el) return;
  el.textContent = msg;
  el.classList.remove('hidden');
  el.classList.add('slide-down');
}

function hideGlobalError(errElId) {
  const el = document.getElementById(errElId);
  if (el) el.classList.add('hidden');
}

function clearLoginErrors() {
  ['login-email-err', 'login-password-err'].forEach(hideFieldError);
  hideGlobalError('login-global-err');
}

function clearRegisterErrors() {
  ['reg-name-err', 'reg-email-err', 'reg-password-err'].forEach(hideFieldError);
  hideGlobalError('reg-global-err');
}

// ══════════════════════════════════════════════════════════════
//  PASSWORD TOGGLE (show/hide)
// ══════════════════════════════════════════════════════════════

function bindPasswordToggle(btnId, inputId, openEyeId, closedEyeId) {
  const btn       = document.getElementById(btnId);
  const input     = document.getElementById(inputId);
  const eyeOpen   = document.getElementById(openEyeId);
  const eyeClosed = document.getElementById(closedEyeId);

  btn.addEventListener('click', () => {
    const isHidden = input.type === 'password';
    input.type = isHidden ? 'text' : 'password';
    eyeOpen.classList.toggle('hidden', isHidden);
    eyeClosed.classList.toggle('hidden', !isHidden);
  });
}

// ══════════════════════════════════════════════════════════════
//  PASSWORD STRENGTH METER
// ══════════════════════════════════════════════════════════════

const STRENGTH_COLORS = ['', 'bg-rose-500', 'bg-orange-400', 'bg-yellow-400', 'bg-emerald-400'];

function measureStrength(pw) {
  let score = 0;
  if (pw.length >= 6)  score++;
  if (pw.length >= 10) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/\d/.test(pw) || /[^a-zA-Z0-9]/.test(pw)) score++;
  return score; // 0–4
}

function updateStrengthBars(pw) {
  const score = measureStrength(pw);
  for (let i = 1; i <= 4; i++) {
    const bar = document.getElementById('bar-' + i);
    if (!bar) continue;
    bar.className = 'h-1 flex-1 rounded-full transition-all';
    bar.classList.add(i <= score ? STRENGTH_COLORS[score] : 'bg-slate-700');
  }
}

document.getElementById('reg-password').addEventListener('input', (e) => {
  updateStrengthBars(e.target.value);
});

// ══════════════════════════════════════════════════════════════
//  AUTH — LOGIN
// ══════════════════════════════════════════════════════════════

document.getElementById('form-login').addEventListener('submit', (e) => {
  e.preventDefault();
  clearLoginErrors();

  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  let   valid    = true;

  if (!email) {
    showFieldError('login-email-err', 'O e-mail é obrigatório.');
    valid = false;
  } else if (!isValidEmail(email)) {
    showFieldError('login-email-err', 'Informe um e-mail válido.');
    valid = false;
  }

  if (!password) {
    showFieldError('login-password-err', 'A senha é obrigatória.');
    valid = false;
  }

  if (!valid) return;

  const db   = loadDB();
  const user = db.users.find(u => u.email.toLowerCase() === email.toLowerCase());

  if (!user) {
    showGlobalError('login-global-err', '❌ E-mail não encontrado. Verifique ou crie uma conta.');
    return;
  }

  if (user.password !== password) {
    showGlobalError('login-global-err', '❌ Senha incorreta. Verifique e tente novamente.');
    return;
  }

  setCurrentUser({ id: user.id, name: user.name, email: user.email });
  initDashboard();
  showScreen('dashboard');
});

// ══════════════════════════════════════════════════════════════
//  AUTH — REGISTER
// ══════════════════════════════════════════════════════════════

document.getElementById('form-register').addEventListener('submit', (e) => {
  e.preventDefault();
  clearRegisterErrors();

  const name     = document.getElementById('reg-name').value.trim();
  const email    = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  let   valid    = true;

  if (!name) {
    showFieldError('reg-name-err', 'O nome é obrigatório.');
    valid = false;
  } else if (name.length < 2) {
    showFieldError('reg-name-err', 'O nome deve ter ao menos 2 caracteres.');
    valid = false;
  }

  if (!email) {
    showFieldError('reg-email-err', 'O e-mail é obrigatório.');
    valid = false;
  } else if (!isValidEmail(email)) {
    showFieldError('reg-email-err', 'Informe um e-mail válido.');
    valid = false;
  }

  if (!password) {
    showFieldError('reg-password-err', 'A senha é obrigatória.');
    valid = false;
  } else if (password.length < 6) {
    showFieldError('reg-password-err', 'A senha deve ter ao menos 6 caracteres.');
    valid = false;
  }

  if (!valid) return;

  const db     = loadDB();
  const exists = db.users.find(u => u.email.toLowerCase() === email.toLowerCase());

  if (exists) {
    showGlobalError('reg-global-err', '⚠ Este e-mail já está cadastrado. Faça login ou use outro e-mail.');
    return;
  }

  const newUser = {
    id:        `user_${Date.now()}`,
    name,
    email,
    password,
    createdAt: new Date().toISOString(),
  };

  db.users.push(newUser);
  saveDB(db);

  setCurrentUser({ id: newUser.id, name: newUser.name, email: newUser.email });
  initDashboard();
  showScreen('dashboard');
});

// ══════════════════════════════════════════════════════════════
//  NAVIGATION LINKS
// ══════════════════════════════════════════════════════════════

document.getElementById('go-register').addEventListener('click', () => {
  clearLoginErrors();
  document.getElementById('form-login').reset();
  showScreen('register');
});

document.getElementById('go-login').addEventListener('click', () => {
  clearRegisterErrors();
  document.getElementById('form-register').reset();
  updateStrengthBars('');
  showScreen('login');
});

// ══════════════════════════════════════════════════════════════
//  LOGOUT
// ══════════════════════════════════════════════════════════════

document.getElementById('btn-logout').addEventListener('click', () => {
  clearCurrentUser();
  activeFilter = 'all';
  document.getElementById('form-login').reset();
  clearLoginErrors();
  showScreen('login');
});

// ══════════════════════════════════════════════════════════════
//  DASHBOARD
// ══════════════════════════════════════════════════════════════

let activeFilter = 'all';

function initDashboard() {
  const user = getCurrentUser();
  if (!user) return;

  const firstName = user.name.split(' ')[0];
  document.getElementById('user-name-display').textContent = firstName;
  document.getElementById('avatar-initial').textContent    = user.name.charAt(0).toUpperCase();

  // Reset filter to "all" on each login
  activeFilter = 'all';
  document.querySelectorAll('.filter-btn').forEach(btn => {
    const isAll = btn.dataset.filter === 'all';
    btn.classList.toggle('active', isAll);
  });

  renderTodos();
}

// ──────────────────────────────────────────────
//  Get todos for the current user
// ──────────────────────────────────────────────

function getUserTodos() {
  const user = getCurrentUser();
  if (!user) return [];
  const db = loadDB();
  // Filter by user.email and sort completed tasks at the end
  return db.todos
    .filter(t => t.userId === user.email)
    .sort((a, b) => {
      if (a.done !== b.done) {
        return a.done ? 1 : -1;
      }
      return b.id - a.id;
    });
}

// ──────────────────────────────────────────────
//  Render todos list
// ──────────────────────────────────────────────

function renderTodos() {
  const all     = getUserTodos();
  const done    = all.filter(t => t.done);
  const pending = all.filter(t => !t.done);

  document.getElementById('stat-total').textContent   = all.length;
  document.getElementById('stat-done').textContent    = done.length;
  document.getElementById('stat-pending').textContent = pending.length;

  let filtered;
  if (activeFilter === 'done')    filtered = done;
  else if (activeFilter === 'pending') filtered = pending;
  else filtered = all;

  const list      = document.getElementById('todo-list');
  const emptyState = document.getElementById('empty-state');

  if (all.length === 0) {
    list.innerHTML = '';
    document.getElementById('empty-state-title').textContent = 'Nenhuma tarefa cadastrada ainda.';
    document.getElementById('empty-state-subtitle').textContent = 'Adicione uma tarefa acima para começar.';
    emptyState.classList.remove('hidden');
    return;
  }

  if (filtered.length === 0) {
    list.innerHTML = '';
    document.getElementById('empty-state-title').textContent = 'Nenhuma tarefa corresponde ao filtro.';
    document.getElementById('empty-state-subtitle').textContent = 'Escolha outro filtro acima.';
    emptyState.classList.remove('hidden');
    return;
  }

  emptyState.classList.add('hidden');

  list.innerHTML = filtered.map(todo => buildTodoHTML(todo)).join('');

  // Bind events
  list.querySelectorAll('.btn-toggle').forEach(btn => {
    btn.addEventListener('click', () => toggleTodo(parseInt(btn.dataset.id)));
  });
  list.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', () => deleteTodo(parseInt(btn.dataset.id)));
  });
}

// ──────────────────────────────────────────────
//  Badge creator based on todo type
// ──────────────────────────────────────────────

function getTypeBadge(type) {
  if (type === 'Trabalho') {
    return `<span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">Trabalho</span>`;
  } else if (type === 'Pessoal') {
    return `<span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">Pessoal</span>`;
  } else if (type === 'Estudos') {
    return `<span class="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Estudos</span>`;
  }
  return '';
}

// ──────────────────────────────────────────────
//  Build a single todo item HTML
// ──────────────────────────────────────────────

function buildTodoHTML(todo) {
  const badgeHTML = getTypeBadge(todo.type);
  const descHTML = todo.description
    ? `<p class="text-xs text-slate-400 mt-1.5 break-words">${escapeHtml(todo.description)}</p>`
    : '';

  const cardStyle = todo.done
    ? 'opacity-60 border-slate-800'
    : 'hover:border-indigo-500/30';

  const textStyle = todo.done
    ? 'line-through text-slate-500'
    : 'text-slate-100 font-semibold';

  const actionButton = todo.done
    ? `<span class="flex items-center gap-1 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg">
         <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
           <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
         </svg>
         Concluída
       </span>`
    : `<button
         class="btn-toggle px-3 py-1.5 text-xs font-semibold bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/35 border border-emerald-500/30 rounded-lg transition-all"
         data-id="${todo.id}">
         Concluir
       </button>`;

  return `
    <div class="glass rounded-xl p-5 flex flex-col gap-3 group todo-item transition-all ${cardStyle}"
         data-id="${todo.id}">

      <div class="flex items-start justify-between gap-4">
        <!-- Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center flex-wrap gap-2 mb-1.5">
            <h3 class="text-sm ${textStyle} break-words">${escapeHtml(todo.title)}</h3>
            ${badgeHTML}
          </div>
          ${descHTML}
          <p class="text-[10px] text-slate-500 mt-2">${formatDate(todo.createdAt)}</p>
        </div>

        <!-- Delete button -->
        <button
          class="btn-delete flex-shrink-0 text-slate-600 hover:text-rose-400 transition-all p-1 rounded-lg hover:bg-rose-500/10"
          data-id="${todo.id}"
          aria-label="Excluir tarefa">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>

      <div class="flex items-center justify-between border-t border-slate-800/40 pt-2">
        <span class="text-[11px] text-slate-500">Status</span>
        ${actionButton}
      </div>
    </div>`;
}

// ══════════════════════════════════════════════════════════════
//  TODOS — CRUD
// ══════════════════════════════════════════════════════════════

// Add todo
document.getElementById('btn-add-todo').addEventListener('click', addTodo);

function addTodo() {
  const titleInput = document.getElementById('new-todo-title');
  const typeSelect = document.getElementById('new-todo-type');
  const descInput  = document.getElementById('new-todo-desc');
  const errEl      = document.getElementById('todo-title-err');
  
  const title       = titleInput.value.trim();
  const type        = typeSelect.value;
  const description = descInput.value.trim();

  if (!title) {
    errEl.classList.remove('hidden');
    titleInput.focus();
    return;
  }

  errEl.classList.add('hidden');

  const user = getCurrentUser();
  const db   = loadDB();

  const newTodo = {
    id:        Date.now(),
    userId:    user.email,
    title,
    type,
    description,
    done:      false,
    createdAt: new Date().toISOString(),
  };

  db.todos.push(newTodo);
  saveDB(db);

  titleInput.value = '';
  descInput.value  = '';
  titleInput.focus();
  renderTodos();
}

// Toggle done/pending
function toggleTodo(id) {
  const db   = loadDB();
  const todo = db.todos.find(t => t.id === id);
  if (!todo) return;
  todo.done = !todo.done;
  saveDB(db);
  renderTodos();
}

// Delete todo
function deleteTodo(id) {
  const db   = loadDB();
  db.todos   = db.todos.filter(t => t.id !== id);
  saveDB(db);
  renderTodos();
}

// ══════════════════════════════════════════════════════════════
//  FILTER TABS
// ══════════════════════════════════════════════════════════════

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter;
    renderTodos();
  });
});

// ══════════════════════════════════════════════════════════════
//  UTILITY — escapeHtml & formatDate
// ══════════════════════════════════════════════════════════════

function escapeHtml(str) {
  return str
    .replace(/&/g,  '&amp;')
    .replace(/</g,  '&lt;')
    .replace(/>/g,  '&gt;')
    .replace(/"/g,  '&quot;')
    .replace(/'/g,  '&#39;');
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleDateString('pt-BR', {
      day: '2-digit', month: 'short', year: 'numeric',
    });
  } catch {
    return iso;
  }
}

// ══════════════════════════════════════════════════════════════
//  INIT — bind toggles & decide first screen
// ══════════════════════════════════════════════════════════════

bindPasswordToggle('toggle-login-pw', 'login-password', 'eye-login-open', 'eye-login-closed');
bindPasswordToggle('toggle-reg-pw',   'reg-password',   'eye-reg-open',   'eye-reg-closed');

(function init() {
  const user = getCurrentUser();
  if (user) {
    initDashboard();
    showScreen('dashboard');
  } else {
    showScreen('login');
  }
})();
