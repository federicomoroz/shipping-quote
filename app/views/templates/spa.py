def render_spa() -> str:
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>shipping-gondola</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=VT323&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #080808;
  --panel: #0d0d0d;
  --border: #1a3300;
  --green: #15ff00;
  --green2: #39ff14;
  --dim: #0a9900;
  --red: #ff3c3c;
  --yellow: #ffcc00;
  --cyan: #00ffcc;
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
body {
  background: var(--bg);
  color: var(--green);
  font-family: 'Share Tech Mono', monospace;
  margin: 0;
  padding: 32px 16px 64px;
}
.crt { max-width: 880px; margin: 0 auto; }
h1, h2 { font-family: 'VT323', monospace; font-weight: normal; letter-spacing: 1px; }
h1 {
  font-size: 2.6rem;
  color: var(--green2);
  text-shadow: 0 0 6px var(--green), 0 0 14px rgba(21,255,0,0.4);
  margin: 0;
}
.cursor { animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
.subtitle { color: var(--dim); margin: 4px 0 28px; text-transform: uppercase; letter-spacing: 1px; font-size: 0.85rem; }
.tabs { display: flex; gap: 12px; margin-bottom: 20px; }
.tab {
  background: transparent; border: 1px solid var(--border); color: var(--dim);
  font-family: 'Share Tech Mono', monospace; padding: 8px 16px; cursor: pointer;
  text-transform: uppercase; letter-spacing: 1px; font-size: 0.85rem;
}
.tab.active, .tab:hover { color: var(--green); border-color: var(--green); text-shadow: 0 0 6px var(--green); }
.tab-panel { display: none; }
.tab-panel.active { display: block; }
.box {
  border: 1px solid var(--border); background: var(--panel);
  padding: 20px 22px; margin-bottom: 22px; border-radius: 2px;
}
.box h2 { font-size: 1.5rem; color: var(--green); margin: 0 0 16px; text-shadow: 0 0 4px rgba(21,255,0,0.5); }
form { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 20px; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--dim); }
input {
  background: #050505; border: 1px solid var(--border); color: var(--green);
  font-family: 'Share Tech Mono', monospace; padding: 8px 10px; font-size: 0.95rem;
}
input:focus { outline: none; border-color: var(--green); box-shadow: 0 0 4px rgba(21,255,0,0.4); }
.run-btn {
  grid-column: 1 / -1; margin-top: 6px; background: transparent; border: 1px solid var(--green);
  color: var(--green); padding: 10px; font-family: 'Share Tech Mono', monospace; font-size: 0.9rem;
  text-transform: uppercase; letter-spacing: 1px; cursor: pointer;
}
.run-btn:hover:not(:disabled) { background: rgba(21,255,0,0.08); text-shadow: 0 0 6px var(--green); }
.run-btn:disabled { opacity: 0.5; cursor: default; }
.error-msg { color: var(--red); margin-top: 12px; font-size: 0.85rem; }
.summary-line { color: var(--cyan); margin: 0 0 16px; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.85rem; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }
.card { border: 1px solid var(--border); padding: 14px; position: relative; }
.card-best { border-color: var(--green); box-shadow: 0 0 8px rgba(21,255,0,0.25); }
.card-error { border-color: rgba(255,60,60,0.4); opacity: 0.75; }
.card-carrier { text-transform: uppercase; letter-spacing: 0.5px; color: var(--dim); font-size: 0.78rem; margin-bottom: 8px; }
.card-amount { font-family: 'VT323', monospace; font-size: 1.9rem; color: var(--green2); }
.card-amount-error { font-family: 'Share Tech Mono', monospace; font-size: 0.95rem; color: var(--red); }
.card-eta { font-size: 0.78rem; color: var(--dim); margin-top: 4px; }
.card-tag {
  position: absolute; top: -9px; right: 10px; background: var(--bg); color: var(--green);
  font-size: 0.65rem; padding: 1px 6px; border: 1px solid var(--green); text-transform: uppercase;
}
.trace-log { max-height: 320px; overflow-y: auto; font-size: 0.78rem; display: flex; flex-direction: column; gap: 3px; }
.trace-line { display: grid; grid-template-columns: 64px 100px 130px 1fr; gap: 10px; padding: 3px 0; border-bottom: 1px dashed rgba(26,51,0,0.6); }
.trace-ms { color: var(--dim); }
.trace-step { text-transform: uppercase; letter-spacing: 0.5px; }
.trace-label { color: var(--green2); }
.trace-detail { color: var(--dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.step-entrada .trace-step, .step-salida .trace-step { color: var(--cyan); }
.step-dominio .trace-step { color: var(--yellow); }
.step-adaptador_primario .trace-step, .step-adaptador_secundario .trace-step { color: var(--green); }
.step-puerto_primario .trace-step, .step-puerto_secundario .trace-step { color: var(--dim); }
.step-caso_de_uso .trace-step { color: var(--green2); }
table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--border); }
th { color: var(--dim); text-transform: uppercase; letter-spacing: 0.5px; font-weight: normal; }
@media (max-width: 560px) {
  form { grid-template-columns: 1fr; }
  .trace-line { grid-template-columns: 56px 90px 1fr; }
  .trace-detail { display: none; }
}
</style>
</head>
<body>
<div class="crt">
  <header>
    <h1>&gt; SHIPPING-GONDOLA<span class="cursor">_</span></h1>
    <p class="subtitle">cotizador de envios &mdash; arquitectura hexagonal en vivo</p>
  </header>

  <nav class="tabs">
    <button class="tab active" data-tab="cotizar">[ COTIZAR ]</button>
    <button class="tab" data-tab="historial">[ HISTORIAL ]</button>
  </nav>

  <section id="tab-cotizar" class="tab-panel active">
    <div class="box form-box">
      <h2>&gt; DATOS DEL PAQUETE</h2>
      <form id="quote-form">
        <label>Peso (kg)<input type="number" step="0.1" name="weight_kg" value="4" required></label>
        <label>Largo (cm)<input type="number" step="1" name="length_cm" value="30" required></label>
        <label>Ancho (cm)<input type="number" step="1" name="width_cm" value="20" required></label>
        <label>Alto (cm)<input type="number" step="1" name="height_cm" value="15" required></label>
        <label>Valor declarado (ARS)<input type="number" step="100" name="declared_value_ars" value="25000" required></label>
        <label>Codigo postal<input type="number" step="1" name="postal_code" value="1425" required></label>
        <button type="submit" class="run-btn">&gt; EJECUTAR CIRCUITO</button>
      </form>
      <p id="form-error" class="error-msg" hidden></p>
    </div>

    <div id="results" class="box results-box" hidden>
      <h2>&gt; COTIZACIONES</h2>
      <p id="summary-line" class="summary-line"></p>
      <div id="cards" class="cards"></div>
    </div>

    <div id="trace-panel" class="box trace-box" hidden>
      <h2>&gt; TRAZA DEL CIRCUITO</h2>
      <div id="trace-log" class="trace-log"></div>
    </div>
  </section>

  <section id="tab-historial" class="tab-panel">
    <div class="box">
      <h2>&gt; HISTORIAL DE COTIZACIONES</h2>
      <table id="history-table">
        <thead><tr><th>Fecha</th><th>CP</th><th>Zona</th><th>Peso ef.</th><th>Mejor</th><th>Monto</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
  </section>
</div>

<script>
const form = document.getElementById('quote-form');
const resultsBox = document.getElementById('results');
const cardsEl = document.getElementById('cards');
const summaryEl = document.getElementById('summary-line');
const traceBox = document.getElementById('trace-panel');
const traceLog = document.getElementById('trace-log');
const errorMsg = document.getElementById('form-error');

const STEP_LABELS = {
  entrada: 'ENTRADA',
  adaptador_primario: 'ADAPTADOR',
  puerto_primario: 'PUERTO',
  caso_de_uso: 'CASO DE USO',
  dominio: 'DOMINIO',
  puerto_secundario: 'PUERTO',
  adaptador_secundario: 'ADAPTADOR',
  salida: 'SALIDA',
};

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorMsg.hidden = true;
  resultsBox.hidden = true;
  traceBox.hidden = true;
  traceLog.innerHTML = '';
  cardsEl.innerHTML = '';

  const fd = new FormData(form);
  const payload = {};
  for (const [k, v] of fd.entries()) payload[k] = parseFloat(v);
  payload.postal_code = parseInt(payload.postal_code, 10);

  const submitBtn = form.querySelector('.run-btn');
  submitBtn.disabled = true;
  submitBtn.textContent = '> EJECUTANDO...';

  try {
    const res = await fetch('/api/quote', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      errorMsg.textContent = '> ERROR: ' + (data.detail || 'solicitud invalida');
      errorMsg.hidden = false;
      return;
    }
    renderResults(data);
    animateTrace(data.trace);
  } catch (err) {
    errorMsg.textContent = '> ERROR DE RED: ' + err.message;
    errorMsg.hidden = false;
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = '> EJECUTAR CIRCUITO';
  }
});

function renderResults(data) {
  const ok = data.results.filter(r => r.ok);
  const bestAmount = ok.length ? Math.min(...ok.map(r => r.amount_ars)) : null;

  summaryEl.textContent = `zona ${data.zone} · peso efectivo ${data.effective_weight_kg.toFixed(1)}kg`;

  data.results.forEach(r => {
    const card = document.createElement('div');
    card.className = 'card' + (r.ok ? '' : ' card-error') + (r.ok && r.amount_ars === bestAmount ? ' card-best' : '');
    if (r.ok) {
      card.innerHTML = `
        <div class="card-carrier">${r.carrier}</div>
        <div class="card-amount">$${r.amount_ars.toLocaleString('es-AR')}</div>
        <div class="card-eta">${r.eta_days} dias habiles</div>
        ${r.amount_ars === bestAmount ? '<div class="card-tag">MEJOR OPCION</div>' : ''}
      `;
    } else {
      card.innerHTML = `
        <div class="card-carrier">${r.carrier}</div>
        <div class="card-amount card-amount-error">SIN RESPUESTA</div>
        <div class="card-eta">${r.error}</div>
      `;
    }
    cardsEl.appendChild(card);
  });

  resultsBox.hidden = false;
}

function animateTrace(trace) {
  traceBox.hidden = false;
  let i = 0;
  function next() {
    if (i >= trace.length) return;
    const entry = trace[i];
    const line = document.createElement('div');
    line.className = 'trace-line step-' + entry.step;
    line.innerHTML = `
      <span class="trace-ms">+${String(Math.round(entry.elapsed_ms)).padStart(4, '0')}ms</span>
      <span class="trace-step">${STEP_LABELS[entry.step] || entry.step}</span>
      <span class="trace-label">${entry.label}</span>
      <span class="trace-detail">${entry.detail}</span>
    `;
    traceLog.appendChild(line);
    traceLog.scrollTop = traceLog.scrollHeight;
    i++;
    const gap = i < trace.length ? Math.min(Math.max((trace[i].elapsed_ms - entry.elapsed_ms) * 2, 40), 260) : 0;
    setTimeout(next, gap);
  }
  next();
}

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
    if (tab.dataset.tab === 'historial') loadHistory();
  });
});

async function loadHistory() {
  const res = await fetch('/api/history');
  const rows = await res.json();
  const tbody = document.querySelector('#history-table tbody');
  tbody.innerHTML = '';
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="6">sin cotizaciones todavia</td></tr>';
    return;
  }
  rows.forEach(r => {
    const tr = document.createElement('tr');
    const fecha = new Date(r.created_at).toLocaleString('es-AR');
    tr.innerHTML = `
      <td>${fecha}</td>
      <td>${r.postal_code}</td>
      <td>${r.zone}</td>
      <td>${r.effective_weight_kg.toFixed(1)}kg</td>
      <td>${r.best_carrier || '-'}</td>
      <td>${r.best_amount_ars ? '$' + r.best_amount_ars.toLocaleString('es-AR') : '-'}</td>
    `;
    tbody.appendChild(tr);
  });
}
</script>
</body>
</html>
"""
