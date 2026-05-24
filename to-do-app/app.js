// BANCO DE DADOS LOCAL
const DB_KEY = 'taskflow_db';
function loadDB() {
  const raw = localStorage.getItem(DB_KEY);
  if (raw) return JSON.parse(raw);
  const initial = { users: [], todos: [] };
  saveDB(initial);
  return initial;
}
function saveDB(db) { localStorage.setItem(DB_KEY, JSON.stringify(db)); }
function getDB() { return loadDB(); }

// SESSÃO
const CURRENT_USER_KEY = 'currentUser';
function getCurrentUser() {
  const raw = localStorage.getItem(CURRENT_USER_KEY);
  return raw ? JSON.parse(raw) : null;
}
function setCurrentUser(user) { localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user)); }
function clearCurrentUser() { localStorage.removeItem(CURRENT_USER_KEY); }

// UI HELPER
function showScreen(screenId) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(`screen-${screenId}`).classList.add('active');
}

// RENDER TODO
function getBadgeClass(type) {
  if (type === 'Trabalho') return 'badge-work';
  if (type === 'Pessoal') return 'badge-personal';
  if (type === 'Estudos') return 'badge-study';
  return 'badge-personal';
}

function renderTodos() {
  const user = getCurrentUser();
  if (!user) return;

  const db = getDB();
  // Filter by userId (e-mail in this case)
  const myTodos = db.todos.filter(t => t.userId === user.email);

  // Sort: pending first, then completed at the bottom
  myTodos.sort((a, b) => {
    if (a.done !== b.done) return a.done ? 1 : -1;
    return b.id - a.id; // newer first
  });

  const list = document.getElementById('todo-list');
  const empty = document.getElementById('empty-state');
  list.innerHTML = '';

  if (myTodos.length === 0) {
    empty.classList.remove('hidden');
  } else {
    empty.classList.add('hidden');
    myTodos.forEach(todo => {
      const isDone = todo.done;
      const card = document.createElement('div');
      card.className = `todo-item glass-card p-4 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${isDone ? 'done' : ''}`;
      
      const content = document.createElement('div');
      content.className = "flex-1";
      content.innerHTML = `
        <div class="flex items-center gap-3 mb-1">
          <span class="todo-title font-semibold text-white text-base">${todo.title}</span>
          <span class="text-xs px-2 py-1 rounded-full font-medium ${getBadgeClass(todo.type)}">${todo.type}</span>
        </div>
        ${todo.description ? `<p class="todo-desc text-slate-400 text-sm mt-1">${todo.description}</p>` : ''}
      `;

      const btnContainer = document.createElement('div');
      if (!isDone) {
        const btn = document.createElement('button');
        btn.className = "btn-primary px-4 py-2 rounded-lg text-sm text-white font-medium whitespace-nowrap";
        btn.textContent = "Concluir";
        btn.onclick = () => {
          todo.done = true;
          // Update DB
          const dbData = getDB();
          const target = dbData.todos.find(t => t.id === todo.id);
          if (target) target.done = true;
          saveDB(dbData);
          renderTodos();
        };
        btnContainer.appendChild(btn);
      } else {
        const span = document.createElement('span');
        span.className = "text-emerald-400 text-sm font-medium";
        span.textContent = "✓ Concluído";
        btnContainer.appendChild(span);
      }

      card.appendChild(content);
      card.appendChild(btnContainer);
      list.appendChild(card);
    });
  }
}

// INIT
document.addEventListener('DOMContentLoaded', () => {
  const user = getCurrentUser();
  if (user) {
    showScreen('dashboard');
    document.getElementById('user-greeting').textContent = `Olá, ${user.name.split(' ')[0]}`;
    renderTodos();
  } else {
    showScreen('login');
  }

  // NAVEGAÇÃO AUTH
  document.getElementById('go-register').onclick = () => showScreen('register');
  document.getElementById('go-login').onclick = () => showScreen('login');

  // REGISTRO
  document.getElementById('form-register').onsubmit = (e) => {
    e.preventDefault();
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const err = document.getElementById('register-error');
    const succ = document.getElementById('register-success');
    
    err.classList.add('hidden');
    succ.classList.add('hidden');

    if (password.length < 6) {
      err.textContent = "A senha deve ter no mínimo 6 caracteres.";
      err.classList.remove('hidden');
      return;
    }

    const db = getDB();
    if (db.users.find(u => u.email === email)) {
      err.textContent = "Este e-mail já está cadastrado.";
      err.classList.remove('hidden');
      return;
    }

    db.users.push({ name, email, password });
    saveDB(db);

    succ.textContent = "Conta criada com sucesso! Redirecionando...";
    succ.classList.remove('hidden');
    setTimeout(() => {
      document.getElementById('form-register').reset();
      showScreen('login');
    }, 1500);
  };

  // LOGIN
  document.getElementById('form-login').onsubmit = (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    const err = document.getElementById('login-error');
    
    err.classList.add('hidden');

    const db = getDB();
    const user = db.users.find(u => u.email === email && u.password === password);

    if (!user) {
      err.textContent = "E-mail ou senha incorretos.";
      err.classList.remove('hidden');
      return;
    }

    setCurrentUser(user);
    document.getElementById('form-login').reset();
    document.getElementById('user-greeting').textContent = `Olá, ${user.name.split(' ')[0]}`;
    showScreen('dashboard');
    renderTodos();
  };

  // LOGOUT
  document.getElementById('btn-logout').onclick = () => {
    clearCurrentUser();
    showScreen('login');
  };

  // NOVA TAREFA
  document.getElementById('form-todo').onsubmit = (e) => {
    e.preventDefault();
    const user = getCurrentUser();
    if (!user) return;

    const title = document.getElementById('todo-title').value.trim();
    const type = document.getElementById('todo-type').value;
    const desc = document.getElementById('todo-desc').value.trim();

    if (!title) return;

    const db = getDB();
    db.todos.push({
      id: Date.now(),
      userId: user.email, // Linking task to user
      title,
      type,
      description: desc,
      done: false
    });
    saveDB(db);

    document.getElementById('form-todo').reset();
    renderTodos();
  };
});
