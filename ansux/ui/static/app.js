const statusGrid = document.getElementById("status-grid");
const systemMetrics = document.getElementById("system-metrics");
const modeBadge = document.getElementById("mode-badge");
const micIndicator = document.getElementById("mic-indicator");
const historyList = document.getElementById("history");
const waveform = document.getElementById("waveform");
const clock = document.getElementById("clock");
const commandForm = document.getElementById("command-form");
const commandInput = document.getElementById("command-input");
const commandSubmit = document.getElementById("command-submit");
const lastReply = document.getElementById("last-reply");
const confirmBanner = document.getElementById("confirm-banner");

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
  micIndicator.textContent = `MIC: ${statuses.microphone || "OFFLINE"} | TEXT: ${data.text_mode ? "ONLINE" : "OFFLINE"}`;

  const sys = data.system || {};
  systemMetrics.innerHTML = `
    <div>CPU: ${sys.cpu_percent ?? "N/A"}%</div>
    <div>RAM: ${sys.memory_percent ?? "N/A"}%</div>
    <div>Platform: ${data.platform || "unknown"}</div>
  `;

  const history = data.history || [];
  historyList.innerHTML = history.slice().reverse().map((item) => {
    const user = item.user ? `<strong>You:</strong> ${escapeHtml(item.user)}` : "";
    const assistant = item.assistant ? `<br><strong>AnshuX:</strong> ${escapeHtml(item.assistant)}` : "";
    return `<li>${user}${assistant}</li>`;
  }).join("") || `<li>No commands yet. Type below or use your microphone.</li>`;

  if (data.listening || data.processing) {
    waveform.classList.add("active");
  } else {
    waveform.classList.remove("active");
  }

  if (data.awaiting_confirmation) {
    confirmBanner.textContent = `Confirmation needed: ${data.awaiting_confirmation} — type yes or no below.`;
    confirmBanner.classList.remove("hidden");
    commandInput.placeholder = "Type yes or no to confirm…";
  } else {
    confirmBanner.classList.add("hidden");
    commandInput.placeholder = "Type a command if the mic is not working… e.g. open vs code, what time is it";
  }

  if (data.last_reply) {
    lastReply.innerHTML = `<strong>AnshuX:</strong> ${escapeHtml(data.last_reply)}`;
  }
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
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

async function sendCommand(text) {
  commandSubmit.disabled = true;
  try {
    const res = await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    if (data.reply) {
      lastReply.innerHTML = `<strong>AnshuX:</strong> ${escapeHtml(data.reply)}`;
    }
    poll();
  } catch (err) {
    lastReply.textContent = "Could not reach AnshuX. Is the server running?";
  } finally {
    commandSubmit.disabled = false;
    commandInput.focus();
  }
}

commandForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = commandInput.value.trim();
  if (!text) return;
  commandInput.value = "";
  sendCommand(text);
});

updateClock();
setInterval(updateClock, 1000);
poll();
setInterval(poll, 1500);
commandInput.focus();
