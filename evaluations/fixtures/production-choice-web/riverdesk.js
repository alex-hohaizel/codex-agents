"use strict";

const element = (id) => document.getElementById(id);
const role = element("role");
const evidence = element("evidence");
const handoff = element("handoff");
const refresh = element("refresh");
const status = element("status");
const revisionKey = (id) => `riverdesk-revision:${id}`;
const currentRevision = (id) => localStorage.getItem(revisionKey(id)) || "1";
let report = reports[0];
let revision;
let conflict;

const reportButtons = reports.map((entry) => {
  const line = document.createElement("li");
  const button = document.createElement("button");
  const reach = document.createElement("span");
  reach.textContent = entry.reach + " · " + entry.id;
  button.type = "button";
  button.append(reach, entry.title);
  button.addEventListener("click", () => select(entry));
  line.append(button);
  element("reports").append(line);
  return button;
});

function updateActions() {
  const operator = role.value === "operator";
  handoff.hidden = !operator;
  handoff.disabled = !operator || !evidence.open || conflict;
  refresh.hidden = !operator || !conflict;
}

function select(entry) {
  report = entry;
  revision = currentRevision(report.id);
  conflict = false;
  evidence.open = false;
  status.textContent = "";
  reportButtons.forEach((button, index) => button.setAttribute("aria-pressed", reports[index] === entry));
  const visible = { "report-id": entry.id, "report-title": entry.title, summary: entry.body,
    source: entry.source, recorded: entry.recorded, confidence: entry.confidence };
  Object.entries(visible).forEach(([id, value]) => { element(id).textContent = value; });
  updateActions();
}

evidence.addEventListener("toggle", updateActions);
role.addEventListener("change", () => {
  status.textContent = role.value === "viewer" ? "Viewer access. You can read evidence." : "Operator access.";
  updateActions();
});

handoff.addEventListener("click", () => {
  if (role.value !== "operator" || !evidence.open || conflict) return;
  if (revision !== currentRevision(report.id)) {
    conflict = true;
    status.textContent = `${report.id} changed while you were reviewing it. Refresh its evidence before sending.`;
    updateActions();
    refresh.focus();
    return;
  }
  const receipt = `Duty review received ${report.id}, revision ${revision}.`;
  localStorage.setItem(`riverdesk-handoff:${report.id}`, receipt);
  status.textContent = receipt;
});

refresh.addEventListener("click", () => {
  select(report);
  status.textContent = `Loaded revision ${revision} for ${report.id}. Review its source again before sending.`;
  evidence.querySelector("summary").focus();
});

select(report);
