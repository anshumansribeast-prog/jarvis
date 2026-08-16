const statusGrid = document.getElementById("status-grid");
const systemMetrics = document.getElementById("system-metrics");
const modeBadge = document.getElementById("mode-badge");
const micIndicator = document.getElementById("mic-indicator");
const historyList = document.getElementById("history");
const waveform = document.getElementById("waveform");
const clock = document.getElementById("clock");

function statusClass(value) {
  if (!value) return "offline";
  const v = String(value).toUpperCase();
  if (v === "ONLINE") return "online";
  if (v === "PARTIAL") return "partial";
  return "offline";
}

function renderStatus(data) {
  const statuses = data.status || {};
  const keys = ["online", "voice", "memory", "ai", "tools", "microphone"];
  statusGrid.innerHTML = keys.map((key) => {
    const value = statuses[key] || "OFFLINE";
    return `<div class="status-card"><div class="label">${key.toUpperCase()}</div><div class="value ${statusClass(value)}">${value}</div></div>`;
  }).join("");

  modeBadge.textContent = (data.mode || "assistant").toUpperCase();
  micIndicator.textContent = `MIC: ${statuses.microphone || "OFFLINE"}`;

  const sys = data.system || {};
  systemMetrics.innerHTML = `
    <div>CPU: ${sys.cpu_percent ?? "N/A"}%</div>
    <div>RAM: ${sys.memory_percent ?? "N/A"}%</div>
    <div>Platform: ${data.platform || "unknown"}</div>
  `;

  const history = data.history || [];
  historyList.innerHTML = history.slice().reverse().map((item) => {
    const user = item.user ? `<strong>You:</strong> ${item.user}` : "";
    const assistant = item.assistant ? `<br><strong>AnshuX:</strong> ${item.assistant}` : "";
    return `<li>${user}${assistant}</li>`;
  }).join("") || `<li>No commands yet.</li>`;

  if (data.listening || data.processing) {
    waveform.classList.add("active");
  } else {
    waveform.classList.remove("active");
  }
}

function updateClock() {
  const now = new Date();
  clock.textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

async function poll() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    renderStatus(data);
  } catch (err) {
    console.error(err);
  }
}

updateClock();
setInterval(updateClock, 1000);
poll();
setInterval(poll, 1500);
