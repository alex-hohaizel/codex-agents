(() => {
  "use strict";
  const { binding, prototype: spec } = JSON.parse(document.getElementById("prototype-data").textContent);
  const screens = new Map(spec.screens.map(screen => [screen.id, screen]));
  const storage = "ux-prototype/" + binding;
  const root = document.getElementById("prototype");
  let current = spec.start, trail = [], notice = "", stored = true;
  function el(tag, content = "", props = {}) {
    const node = document.createElement(tag);
    for (const [name, val] of Object.entries(props)) node.setAttribute(name, val);
    node.textContent = content;
    return node;
  }
  function resume() {
    try {
      const saved = localStorage.getItem(storage);
      if (!saved) return;
      const raw = JSON.parse(saved);
      if (!Array.isArray(raw) || raw.length > 160) throw new Error("Invalid walkthrough");
      let point = spec.start;
      for (const row of raw) {
        if (!row || row.from !== point) throw new Error("Discontinuous walkthrough");
        const action = screens.get(point).actions.find(a => a.id === row.action);
        if (!action || action.to !== row.to) throw new Error("Unknown branch");
        point = row.to;
      }
      trail = raw.map(({from, action, to}) => ({from, action, to}));
      current = point;
      if (trail.length) notice = "Restored this walkthrough on this browser.";
    } catch { notice = "Could not restore the walkthrough. Started at its first screen."; }
  }
  function save() {
    try { localStorage.setItem(storage, JSON.stringify(trail)); }
    catch { stored = false; }
  }
  function download() {
    const receipt = {schema: "codex-agents.ux-prototype-session/1", prototype: spec.id, binding,
      screen: current, state: screens.get(current).state, transitions: trail, sources: spec.sources,
      mode: "simulated-interaction", accepted: false};
    const blob = new Blob([JSON.stringify(receipt, null, 2) + "\n"], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const a = el("a", "", {href: url, download: spec.id + "-walkthrough.json"});
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1200);
  }
  const states = {normal: "In review", pending: "Uncertain", conflict: "Needs a decision", success: "Complete"};
  function render(focus = false) {
    root.replaceChildren();
    const head = el("header", "", {class: "mast"});
    const identity = el("div", "", {class: "identity"});
    identity.append(el("span", "UX / REVIEW", {class: "eyebrow"}), el("p", spec.title, {class: "title"}));
    head.append(identity, el("span", "Interactive prototype", {class: "tag"}));
    const shell = el("main", "", {class: "shell"});
    const timeline = el("aside", "", {class: "side", "aria-label": "Walkthrough history"});
    timeline.append(el("p", "Walkthrough", {class: "eyebrow"}), el("p", spec.summary, {class: "summary"}));
    const history = el("ol", "", {class: "history"});
    for (const item of [spec.start, ...trail.map(t => t.to)].slice(-10)) history.append(el("li", screens.get(item).label));
    history.lastElementChild.setAttribute("aria-current", "step");
    timeline.append(history, el("div", notice || (!stored ? "This browser could not save your walkthrough." : ""),
      {role: "status", class: "notice"}));
    const reset = el("button", "Restart walkthrough", {type: "button", class: "quiet"});
    reset.addEventListener("click", () => { trail = []; current = spec.start; notice = "Walkthrough restarted."; save(); render(true); });
    timeline.append(reset);
    const screen = screens.get(current);
    const section = el("section", "", {class: "panel", "aria-labelledby": "screen-title", "data-state": screen.state});
    const marker = el("div", "", {class: "marker"});
    marker.append(el("span", screen.label, {class: "eyebrow"}), el("span", states[screen.state], {class: "state"}));
    const title = el("h1", screen.heading, {id:"screen-title", tabindex:"-1"});
    section.append(marker, title, el("p", screen.body, {class: "body"}));
    if (screen.details?.length) {
      const grid = el("dl", "", {class:"details"});
      for (const row of screen.details) {
        const item = el("div"); item.append(el("dt", row.label), el("dd", row.value)); grid.append(item);
      }
      section.append(grid);
    }
    const fields = new Map();
    for (const f of screen.fields ?? []) {
      const group = el("div", "", {class:"field"});
      const id = "field-" + f.id;
      const control = f.type === "choice" ? el("select", "", {id}) :
        el("input", "", {id, type: f.type === "check" ? "checkbox" : "text"});
      if (f.type === "text") control.setAttribute("maxlength", "200");
      if (f.type === "choice") {
        control.append(el("option", "Choose an option", {value:""}));
        f.options.forEach(label => control.append(el("option", label, {value:label})));
      }
      const label = el("label", f.label, {for:id});
      if (f.type === "check") {
        group.classList.add("check"); label.prepend(control); group.append(label);
      } else group.append(label, control);
      if (f.help) {
        control.setAttribute("aria-describedby", id + "-help");
        group.append(el("small", f.help, {id:id+"-help"}));
      }
      fields.set(f.id, {f,control});
      group.dataset.field = f.id;
      section.append(group);
    }
    const error = el("p", "", {role:"alert", class: "error"});
    section.append(error);
    const actions = el("div", "", {class:"actions"});
    for (const action of screen.actions) {
      const button = el("button", action.label, {type:"button", class:action.style ?? "secondary","data-action":action.id});
      button.addEventListener("click", () => {
        error.textContent = "";
        for (const {control} of fields.values()) control.removeAttribute("aria-invalid");
        for (const field of action.requires ?? []) {
          const {f, control} = fields.get(field);
          if (f.type === "check" ? !control.checked : !control.value.trim()) {
            error.textContent = "Complete this step: " + f.label;
            control.setAttribute("aria-invalid", "true"); control.focus(); return;
          }
        }
        if (trail.length >= 160) { error.textContent = "Walkthrough limit reached. Download the current evidence or restart."; return; }
        trail.push({from:current, action:action.id, to:action.to}); current = action.to;
        notice = ""; save(); render(true);
      });
      actions.append(button);
    }
    const exportButton = el("button", "Download walkthrough", {type:"button", class:"quiet"});
    exportButton.addEventListener("click", download);
    actions.append(exportButton); section.append(actions);
    const sources = el("details", "", {class:"sources"});
    sources.append(el("summary", "Design and experience references"));
    for (const link of screen.refs) {
      const ref = spec.sources.find(source => source.id === link.source);
      const block = el("blockquote", link.excerpt);
      block.append(el("cite", ref.kind + " · " + ref.path));
      sources.append(block);
    }
    section.append(sources);
    shell.append(section, timeline);
    const foot = el("footer", "Local walkthrough. Forms simulate interaction; no provider or product state changes.", {class:"foot"});
    root.append(head, shell, foot);
    if (focus) title.focus();
  }
  resume();
  render();
})();
