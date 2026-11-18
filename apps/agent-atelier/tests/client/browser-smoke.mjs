import { spawn } from "node:child_process";
import { mkdir, mkdtemp, writeFile, realpath } from "node:fs/promises";
import { tmpdir } from "node:os";
import { resolve, join } from "node:path";
import { createHash } from "node:crypto";

const origin = process.env.ATELIER_TEST_ORIGIN ?? "http://127.0.0.1:4317";
// The test harness mints this short-lived fixture token without printing it.
// Never include it in report metadata, screenshots, or persisted URLs.
const launchToken = process.env.ATELIER_TEST_LAUNCH_TOKEN;
const reportDir =
  process.env.ATELIER_BROWSER_REPORT_DIR ??
  (await mkdtemp(join(tmpdir(), "atelier-client-review-")));
await mkdir(reportDir, { recursive: true });
const profile = await mkdtemp(join(tmpdir(), "atelier-browser-profile-"));
const fixtureRoot = await realpath(
  await mkdtemp(join(tmpdir(), "atelier-ui-fixture-")),
);
await writeFile(
  join(fixtureRoot, "AGENTS.md"),
  "# UI test project\n\nPreserve this isolated fixture. Only prepare a read-only task; do not dispatch.\n",
);
const fixtureNextAction =
  "Inspect the isolated fixture instructions and return a short source-backed report.";
await writeFile(
  join(fixtureRoot, "README.md"),
  `# Browser acceptance fixture\n\nThis is a local synthetic source for project-binding and task-preparation UI checks.\n\n## Next action\n\n- ${fixtureNextAction}\n`,
);
const browser = spawn(
  process.env.ATELIER_TEST_CHROME ??
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-sync",
    "--disable-extensions",
    "--hide-scrollbars",
    "--remote-debugging-pipe",
    `--user-data-dir=${profile}`,
  ],
  { stdio: ["ignore", "pipe", "pipe", "pipe", "pipe"] },
);
const pending = new Map();
let seq = 0,
  buffer = "",
  stderr = "";
const exceptions = [],
  screenshots = [],
  checks = [],
  requestFailures = [];
browser.stderr.on("data", (chunk) => {
  stderr = (stderr + chunk).slice(-3000);
});
browser.stdio[4].on("data", (bytes) => {
  buffer += bytes.toString();
  while (buffer.includes("\0")) {
    const end = buffer.indexOf("\0"),
      raw = buffer.slice(0, end);
    buffer = buffer.slice(end + 1);
    if (!raw) continue;
    const message = JSON.parse(raw);
    if (message.id && pending.has(message.id)) {
      const call = pending.get(message.id);
      pending.delete(message.id);
      clearTimeout(call.timer);
      message.error
        ? call.reject(Error(JSON.stringify(message.error)))
        : call.resolve(message.result);
    } else if (message.method === "Runtime.exceptionThrown")
      exceptions.push(message.params);
    else if (
      message.method === "Network.loadingFailed" &&
      !message.params.canceled
    )
      requestFailures.push(message.params);
  }
});
function call(method, params = {}, sessionId) {
  return new Promise((resolveCall, reject) => {
    const id = ++seq;
    const timer = setTimeout(() => {
      pending.delete(id);
      reject(Error(`CDP timeout: ${method}`));
    }, 15000);
    pending.set(id, { resolve: resolveCall, reject, timer });
    browser.stdio[3].write(
      `${JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) })}\0`,
    );
  });
}
const pause = (ms) => new Promise((r) => setTimeout(r, ms));
let session;
async function evaluate(expression) {
  const result = await call(
    "Runtime.evaluate",
    { expression, returnByValue: true, awaitPromise: true },
    session,
  );
  if (result.exceptionDetails)
    throw Error(
      result.exceptionDetails.exception?.description ??
        result.exceptionDetails.text,
    );
  return result.result.value;
}
async function waitFor(expression, message, timeout = 15000) {
  const until = Date.now() + timeout;
  while (Date.now() < until) {
    if (await evaluate(expression)) return;
    await pause(150);
  }
  throw Error(message);
}
async function screenshot(name, width, height, mobile = false) {
  await call(
    "Emulation.setDeviceMetricsOverride",
    { width, height, deviceScaleFactor: 1, mobile },
    session,
  );
  await pause(180);
  const metrics = await evaluate(
    `({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,height:innerHeight,title:document.title,h1:document.querySelector('h1')?.textContent,demo:!!document.querySelector('.demo-strip'),text:document.body.innerText.slice(0,600),visiblePanels:[...document.querySelectorAll('.panel__heading h2')].map(e=>e.textContent)})`,
  );
  const result = await call(
    "Page.captureScreenshot",
    { format: "png", captureBeyondViewport: false },
    session,
  );
  const bytes = Buffer.from(result.data, "base64");
  await writeFile(join(reportDir, name), bytes);
  screenshots.push({
    file: name,
    sha256: createHash("sha256").update(bytes).digest("hex"),
    viewport: [width, height],
    mobile,
    metrics,
  });
  checks.push({
    name: `No page overflow: ${name}`,
    pass: metrics.scrollWidth === metrics.width,
  });
}
async function inputValue(selector, value) {
  return evaluate(
    `(()=>{const e=document.querySelector(${JSON.stringify(selector)});if(!e)throw Error('Input not found');Object.getOwnPropertyDescriptor(e.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype,'value').set.call(e,${JSON.stringify(value)});e.dispatchEvent(new Event('input',{bubbles:true}));return true})()`,
  );
}
async function clickText(selector, value) {
  return evaluate(
    `(()=>{const e=[...document.querySelectorAll(${JSON.stringify(selector)})].find(e=>e.innerText.includes(${JSON.stringify(value)}));if(!e)throw Error('Button not found: '+${JSON.stringify(value)});e.click();return true})()`,
  );
}
try {
  const target = await call("Target.createTarget", { url: "about:blank" });
  const attached = await call("Target.attachToTarget", {
    targetId: target.targetId,
    flatten: true,
  });
  session = attached.sessionId;
  await call("Page.enable", {}, session);
  await call("Runtime.enable", {}, session);
  await call("Network.enable", {}, session);
  await call(
    "Emulation.setDeviceMetricsOverride",
    { width: 1440, height: 1080, deviceScaleFactor: 1, mobile: false },
    session,
  );
  await call("Page.navigate", { url: `${origin}/?demo=1` }, session);
  await pause(900);
  checks.push({
    name: "Explicit demonstration marker",
    pass: await evaluate(
      `document.querySelector('.demo-strip')?.textContent.includes('вигадані') ?? false`,
    ),
  });
  await screenshot("reference-workbench-1440.png", 1440, 1080);
  await screenshot("reference-workbench-1920.png", 1920, 1200);
  await screenshot("reference-workbench-390.png", 390, 1000, true);
  await evaluate(
    `(()=>{const b=document.querySelector('.mobile-menu');b.focus();b.click()})()`,
  );
  await pause(80);
  const drawer = await evaluate(`(()=>{
    const drawer=document.querySelector('#project-navigation-drawer');
    return {open:drawer?.getAttribute('aria-modal')==='true',routes:[...new Set([...drawer.querySelectorAll('[data-view]')].map(e=>e.dataset.view))],focusInside:drawer.contains(document.activeElement)};
  })()`);
  checks.push({
    name: "Mobile drawer exposes all eleven existing views and receives focus",
    pass: drawer.open && drawer.focusInside && drawer.routes.length === 11,
  });
  await evaluate(
    `(()=>{const d=document.querySelector('#project-navigation-drawer');const a=[...d.querySelectorAll('button:not(:disabled),a[href],select:not(:disabled),[tabindex="0"]')].filter(e=>e.getClientRects().length);a.at(-1)?.focus()})()`,
  );
  await call(
    "Input.dispatchKeyEvent",
    { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 },
    session,
  );
  await call(
    "Input.dispatchKeyEvent",
    { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 },
    session,
  );
  checks.push({
    name: "Mobile drawer wraps keyboard focus instead of losing controls behind it",
    pass: await evaluate(
      `(()=>{const d=document.querySelector('#project-navigation-drawer');return document.activeElement===d.querySelector('button:not(:disabled)')})()`,
    ),
  });
  await call(
    "Input.dispatchKeyEvent",
    {
      type: "keyDown",
      key: "Escape",
      code: "Escape",
      windowsVirtualKeyCode: 27,
    },
    session,
  );
  await call(
    "Input.dispatchKeyEvent",
    { type: "keyUp", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27 },
    session,
  );
  await pause(80);
  checks.push({
    name: "Escape closes the mobile drawer and returns focus to its trigger",
    pass: await evaluate(
      `!document.querySelector('.atelier-shell').classList.contains('nav-open')&&document.activeElement===document.querySelector('.mobile-menu')`,
    ),
  });
  for (const view of ["settings", "jobs", "skills", "context"]) {
    await evaluate(
      `(()=>{const b=document.querySelector('.mobile-menu');b.focus();b.click()})()`,
    );
    await pause(40);
    await evaluate(
      `document.querySelector('#project-navigation-drawer [data-view="${view}"]').click()`,
    );
    await pause(60);
    checks.push({
      name: `Mobile navigation opens ${view} and dismisses the drawer`,
      pass: await evaluate(
        `document.querySelector('#main-content')?.dataset.currentView===${JSON.stringify(view)}&&!document.querySelector('.atelier-shell').classList.contains('nav-open')`,
      ),
    });
  }
  checks.push({
    name: "Context view retains full record and exposes declared-binding limits",
    pass: await evaluate(
      `!!document.querySelector('.context-coverage-panel')&&!!document.querySelector('.context-reader-grid .code-viewer')&&document.querySelector('.context-coverage-summary')?.innerText.includes('не доводить')`,
    ),
  });
  await call(
    "Emulation.setDeviceMetricsOverride",
    { width: 1440, height: 1080, deviceScaleFactor: 1, mobile: false },
    session,
  );
  await call(
    "Page.navigate",
    {
      url: launchToken
        ? `${origin}/#atelier_launch=${encodeURIComponent(launchToken)}`
        : `${origin}/`,
    },
    session,
  );
  await pause(1100);
  if (launchToken)
    checks.push({
      name: "Launcher fragment consumed before rendering",
      pass: await evaluate(`!location.hash.includes('atelier_launch')`),
    });
  checks.push({
    name: "Live view is not demonstration",
    pass: await evaluate(`!document.querySelector('.demo-strip')`),
  });
  const projects = await evaluate(
    `fetch('/api/v1/bootstrap',{headers:{'X-Atelier-CSRF':sessionStorage.getItem('atelier.session.csrf.v1')||''}}).then(r=>r.json()).then(x=>x.projects)`,
  );
  if (process.env.ATELIER_TEST_ROOT) {
    const binding = await evaluate(
      `(async()=>{const b=await fetch('/api/v1/bootstrap',{headers:{'X-Atelier-CSRF':sessionStorage.getItem('atelier.session.csrf.v1')||''}}).then(r=>r.json());const command=async(operation,payload)=>{let r=await fetch('/api/v1/commands',{method:'POST',headers:{'Content-Type':'application/json','X-Atelier-CSRF':b.csrf_token},body:JSON.stringify({command_id:crypto.randomUUID(),operation,payload})});let body=await r.json();if(!r.ok)throw Error(JSON.stringify(body.error));return body.result;};const root=${JSON.stringify(process.env.ATELIER_TEST_ROOT)};const existing=b.projects.find(p=>p.root===root);if(existing)return existing;const preview=await command('project.preview',{root});const result=await command('project.bind',{preview_id:preview.preview_id,name:'Agent System'});return result.project;})()`,
    );
    checks.push({
      name: "Explicit current-repository binding",
      pass: Boolean(binding?.id),
      project_id: binding?.id,
    });
    await call(
      "Page.navigate",
      { url: `${origin}/?project=${encodeURIComponent(binding.id)}` },
      session,
    );
    await pause(1300);
    checks.push({
      name: "Live project opens the operator work map, with technical sources behind an explicit tab",
      pass: await evaluate(
        `!!document.querySelector('.operator-canvas')&&!document.querySelector('.operator-canvas .code-viewer')&&!document.querySelector('.task-ribbon')&&document.querySelector('[data-operator-mode="work"]')?.getAttribute('aria-pressed')==='true'`,
      ),
    });
    const actualWorkSelection = await evaluate(
      `(()=>{const button=document.querySelector('.operator-work-lane>button');if(!button)return {available:false};button.click();return {available:true}})()`,
    );
    const laneDisclosure = await evaluate(
      `(()=>{const b=document.querySelector('[data-expand-work-lane]');if(!b)return {available:false};const lane=b.closest('.operator-work-lane');const count=lane.querySelectorAll('.operator-work-node').length;b.click();return {available:true,selector:'.operator-work-lane--'+b.dataset.expandWorkLane,before:count}})()`,
    );
    if (laneDisclosure.available) {
      await pause(80);
      checks.push({
        name: "All loaded source work in a lane is reachable beyond its collapsed preview",
        pass: await evaluate(
          `(()=>{const lane=document.querySelector(${JSON.stringify(laneDisclosure.selector)});return lane.querySelector('[data-expand-work-lane]')?.getAttribute('aria-expanded')==='true'&&lane.querySelectorAll('.operator-work-node').length>${Number(laneDisclosure.before)}})()`,
        ),
      });
    }
    if (actualWorkSelection.available) {
      await pause(80);
      checks.push({
        name: "Selecting a real recorded work node opens its focused human result",
        pass: await evaluate(
          `!!document.querySelector('.operator-work-lane>button.is-selected')&&document.querySelector('.operator-focus h3')?.textContent===document.querySelector('.operator-work-lane>button.is-selected strong')?.textContent`,
        ),
      });
    }
    const coldSourceCount = await evaluate(
      `(()=>{window.__operatorColdCommands=[];const original=window.fetch;window.__restoreOperatorFetch=()=>{window.fetch=original;delete window.__restoreOperatorFetch};window.fetch=async(...args)=>{const url=typeof args[0]==='string'?args[0]:args[0]?.url;if(String(url).endsWith('/api/v1/commands')&&typeof args[1]?.body==='string'){try{const body=JSON.parse(args[1].body);window.__operatorColdCommands.push({operation:body.operation,max_pages:body.payload?.max_pages})}catch{}}return original.apply(window,args)};const count=Number(document.querySelector('.operator-work-map')?.dataset.sourceWorkCount??0);document.querySelector('[data-open-native-history]').click();return count})()`,
    );
    await pause(700);
    checks.push({
      name: "History action reveals its region and moves keyboard focus to visible feedback",
      pass: await evaluate(
        `(()=>{const region=document.querySelector('#operator-native-history');const rect=region.getBoundingClientRect();return region.querySelector('.operator-history-toggle')?.getAttribute('aria-expanded')==='true'&&document.activeElement===region&&rect.top>=0&&rect.top<innerHeight})()`,
      ),
    });
    const coldButtonAvailable = await evaluate(
      `!!document.querySelector('[data-discover-native-history]')`,
    );
    if (coldButtonAvailable) {
      await evaluate(
        `document.querySelector('[data-discover-native-history]').click()`,
      );
      let discoveryChecked = false;
      for (let attempt = 0; attempt < 60; attempt++) {
        await pause(200);
        discoveryChecked = await evaluate(
          `fetch('/api/v1/portfolio').then(r=>r.json()).then(p=>!!p.checked_at&&p.status!=='not_checked')`,
        );
        if (discoveryChecked) break;
      }
      await pause(300);
      checks.push({
        name: "Cold history invokes the bounded refresh operation rather than rereading empty cache",
        pass: await evaluate(
          `window.__operatorColdCommands.some(c=>c.operation==='portfolio.refresh'&&c.max_pages===20)`,
        ),
      });
      checks.push({
        name: "Cold discovery returns an observed map or explicit gap and retains the fresh source-work map",
        pass:
          discoveryChecked &&
          (await evaluate(
            `Number(document.querySelector('.operator-work-map')?.dataset.sourceWorkCount??0)===${Number(coldSourceCount)}&&!!document.querySelector('#operator-native-history .work-map,#operator-native-history .empty')`,
          )),
      });
    }
    await evaluate(
      `window.__restoreOperatorFetch?.();delete window.__operatorColdCommands;document.querySelector('#main-content').scrollTo({top:0,behavior:'instant'})`,
    );
    await screenshot("operator-repository-1440.png", 1440, 1080);
    await screenshot("operator-repository-1920.png", 1920, 1200);
    await screenshot("operator-repository-390.png", 390, 1000, true);
    await call(
      "Emulation.setDeviceMetricsOverride",
      { width: 1440, height: 1080, deviceScaleFactor: 1, mobile: false },
      session,
    );
    await waitFor(
      `document.querySelector('.operator-action>.button')?.disabled===false`,
      "Next action unavailable after native discovery",
    );
    const expectedNextAction = await evaluate(
      `(async()=>{const data=await fetch('/api/v1/projects/'+encodeURIComponent(${JSON.stringify(binding.id)})+'/workspace').then(r=>r.json());return data.current_checkpoint?.next??data.next_actions?.[0]?.text??document.querySelector('#operator-next-title').textContent})()`,
    );
    await evaluate(
      `document.querySelector('.operator-action>.button').click()`,
    );
    await waitFor(
      "!!document.querySelector('dialog textarea')",
      "Next-action task did not open",
    );
    checks.push({
      name: "Next useful action opens scoped preparation with the full objective",
      pass: await evaluate(
        `document.querySelector('dialog')?.open===true&&document.querySelector('dialog textarea')?.value===${JSON.stringify(expectedNextAction)}`,
      ),
    });
    await evaluate(
      `document.querySelector('dialog .modal__header .icon-button')?.click()`,
    );
    await evaluate(
      `document.querySelector('[data-operator-mode="sources"]').click()`,
    );
    await pause(300);
    checks.push({
      name: "Live source panel populated",
      pass: await evaluate(
        `document.querySelector('.code-viewer__scroll')?.innerText.length>100`,
      ),
    });
    await screenshot("live-repository-1440.png", 1440, 1080);
    for (const [view, selector] of [
      ["requirements", "Вимоги"],
      ["context", "Контекст"],
      ["evidence", "Докази"],
    ]) {
      await evaluate(
        `(()=>{const b=[...document.querySelectorAll('.project-navigation button')].find(b=>b.innerText.includes(${JSON.stringify(selector)}));b?.click();})()`,
      );
      await pause(200);
      await screenshot(`live-${view}-1440.png`, 1440, 1080);
    }
    await evaluate(
      `(()=>{const b=[...document.querySelectorAll('.platform-navigation button')].find(b=>b.innerText.includes('Агенти'));b?.click();})()`,
    );
    await pause(200);
    await screenshot("live-skills-1440.png", 1440, 1080);
    checks.push({
      name: "Actual skill catalog rendered",
      pass: await evaluate(
        `document.querySelectorAll('.skill-list>button').length>20`,
      ),
    });
  } else
    checks.push({
      name: "No automatic project binding",
      pass: Array.isArray(projects),
    });
  await call("Page.navigate", { url: `${origin}/?demo=1` }, session);
  await pause(500);
  await evaluate(
    `window.dispatchEvent(new KeyboardEvent('keydown',{key:'k',ctrlKey:true,bubbles:true}))`,
  );
  await pause(100);
  checks.push({
    name: "Keyboard command palette",
    pass: await evaluate(`document.querySelector('dialog')?.open===true`),
  });
  await evaluate(`document.querySelector('dialog .icon-button')?.click()`);
  for (const locale of ["uk", "en", "de", "it", "es", "fr", "zh-CN"]) {
    await call(
      "Emulation.setDeviceMetricsOverride",
      { width: 1440, height: 1080, deviceScaleFactor: 1, mobile: false },
      session,
    );
    await call(
      "Page.navigate",
      { url: `${origin}/?demo=1&locale=${locale}` },
      session,
    );
    await pause(350);
    checks.push({
      name: `Locale ${locale} loads`,
      pass: await evaluate(
        `document.documentElement.lang===${JSON.stringify(locale)}`,
      ),
    });
    await screenshot(`locale-${locale}-1440.png`, 1440, 1080);
  }
  await call("Page.navigate", { url: `${origin}/?locale=uk` }, session);
  await pause(700);
  await evaluate(
    `document.querySelector('button[aria-label="Підключити проєкт"]').click()`,
  );
  await pause(100);
  checks.push({
    name: "Binding dialog opens",
    pass: await evaluate(`document.querySelector('dialog')?.open===true`),
  });
  await inputValue("dialog input", fixtureRoot);
  await waitFor(
    `[...document.querySelectorAll('dialog .modal__footer button')].some(b=>!b.disabled&&b.innerText.includes('Перевірити папку'))`,
    "The project preview button did not become ready",
  );
  await clickText("dialog .modal__footer button", "Перевірити папку");
  await waitFor(
    `!!document.querySelector('.binding-preview')`,
    "The project preview did not load",
  );
  checks.push({
    name: "Read-only project preview rendered",
    pass: await evaluate(`!!document.querySelector('.binding-preview')`),
  });
  await clickText("dialog .modal__footer button", "Підключити цей проєкт");
  await pause(900);
  checks.push({
    name: "Project connects through UI",
    pass: await evaluate(
      `fetch('/api/v1/bootstrap',{headers:{'X-Atelier-CSRF':sessionStorage.getItem('atelier.session.csrf.v1')||''}}).then(r=>r.json()).then(x=>x.projects.some(p=>p.root===${JSON.stringify(fixtureRoot)}))`,
    ),
  });
  await waitFor(
    `document.querySelector('#operator-next-title')?.textContent===${JSON.stringify(fixtureNextAction)}&&document.querySelector('.operator-action>.button')?.disabled===false`,
    "The declared fixture next action did not load",
  );
  const fixtureBeforePrepare = await evaluate(
    `fetch('/api/v1/bootstrap',{headers:{'X-Atelier-CSRF':sessionStorage.getItem('atelier.session.csrf.v1')||''}}).then(r=>r.json()).then(data=>({projectId:data.projects.find(p=>p.root===${JSON.stringify(fixtureRoot)}).id, jobs:data.jobs.length}))`,
  );
  await evaluate(`document.querySelector('.operator-action>.button').click()`);
  await waitFor(
    "!!document.querySelector('dialog textarea')",
    "Fixture next-action task did not open",
  );
  checks.push({
    name: "A declared next action prefills the exact objective",
    pass: await evaluate(
      `document.querySelector('dialog textarea')?.value===${JSON.stringify(fixtureNextAction)}`,
    ),
  });
  const editedObjective =
    fixtureNextAction + " Include the exact source filename.";
  const acceptance =
    "Return the exact source filename and explain its preservation requirement.";
  await inputValue("dialog textarea", editedObjective);
  await evaluate(
    `(()=>{const field=document.querySelectorAll('dialog textarea')[1];const set=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;set.call(field,${JSON.stringify(acceptance)});field.dispatchEvent(new Event('input',{bubbles:true}));})()`,
  );
  await waitFor(
    `[...document.querySelectorAll('dialog .modal__footer button')].some(b=>!b.disabled&&b.innerText.includes('Переглянути маршрут'))`,
    "The next-action objective and acceptance did not enable route review",
  );
  await clickText("dialog .modal__footer button", "Переглянути маршрут");
  await waitFor(
    `[...document.querySelectorAll('dialog .modal__footer button')].some(b=>!b.disabled&&b.innerText.includes('Підготувати виконання'))`,
    "The next action route did not finish review",
    45000,
  );
  await clickText("dialog .modal__footer button", "Підготувати виконання");
  await waitFor(
    `document.querySelector('dialog h2')?.textContent.includes('підготовлено')`,
    "The next action was not prepared",
  );
  checks.push({
    name: "The edited next action and acceptance are saved under the selected project without dispatch",
    pass: await evaluate(
      `fetch('/api/v1/bootstrap',{headers:{'X-Atelier-CSRF':sessionStorage.getItem('atelier.session.csrf.v1')||''}}).then(r=>r.json()).then(data=>data.jobs.length===${fixtureBeforePrepare.jobs}&&data.tasks.some(task=>task.project_id===${JSON.stringify(fixtureBeforePrepare.projectId)}&&task.objective===${JSON.stringify(editedObjective)}&&task.acceptance===${JSON.stringify(acceptance)}&&task.scope==='read-only'&&task.status==='prepared'))`,
    ),
  });
  await screenshot("prepared-task-review-1440.png", 1440, 1080);
  checks.push({
    name: "Unreviewed prepared scope cannot dispatch",
    pass: await evaluate(
      `[...document.querySelectorAll('dialog .modal__footer button')].find(b=>b.innerText.includes('Запустити'))?.disabled===true`,
    ),
  });
  await evaluate(
    `document.querySelector('dialog .modal__header .icon-button')?.click()`,
  );
  await pause(100);
  await clickText(".platform-navigation button", "Агенти");
  await pause(150);
  await clickText(".constructor-actions button", "Створити спеціаліста");
  await pause(100);
  await inputValue(
    "dialog textarea",
    "A specialist for reviewing source-backed interface and media fidelity across product stages.",
  );
  await clickText("dialog .modal__footer button", "Підготувати виконання");
  await pause(150);
  checks.push({
    name: "Constructor opens scoped M1 planning task",
    pass: await evaluate(
      `document.querySelector('dialog')?.innerText.includes('agent-foundry')&&document.querySelector('dialog')?.innerText.includes('планування M1')`,
    ),
  });
  await evaluate(
    `document.querySelector('dialog .modal__header .icon-button')?.click()`,
  );
  await call(
    "Emulation.setDeviceMetricsOverride",
    { width: 390, height: 1000, deviceScaleFactor: 1, mobile: true },
    session,
  );
  await call("Page.navigate", { url: `${origin}/?demo=1&locale=uk` }, session);
  await pause(350);
  await screenshot("mobile-final-390.png", 390, 1000, true);
  await evaluate(`document.querySelector('.mobile-menu').click()`);
  await pause(100);
  checks.push({
    name: "Mobile navigation opens",
    pass: await evaluate(
      `getComputedStyle(document.querySelector('.navigation-rail')).display!=='none'`,
    ),
  });
  await screenshot("mobile-navigation-390.png", 390, 1000, true);
  const report = {
    schema: "atelier-client-browser-review/1",
    origin,
    reportDir,
    profile,
    checks,
    screenshots,
    runtimeExceptions: exceptions,
    requestFailures,
    limits: [
      "Actual local browser and service/source checks; no model task started by this script.",
      "Screenshots require visual review, not only DOM counts.",
      "Not full accessibility, cross-browser or human-usability certification.",
    ],
    stderr,
  };
  await writeFile(
    join(reportDir, "browser-review.json"),
    `${JSON.stringify(report, null, 2)}\n`,
  );
  console.log(
    JSON.stringify({
      reportDir,
      screenshots: screenshots.map((s) => ({
        file: s.file,
        viewport: s.viewport,
        width: s.metrics.width,
        scrollWidth: s.metrics.scrollWidth,
      })),
      checks,
      runtimeExceptions: exceptions.length,
      requestFailures: requestFailures.length,
    }),
  );
  if (checks.some((c) => !c.pass) || exceptions.length) process.exitCode = 1;
} catch (error) {
  await writeFile(
    join(reportDir, "browser-review.json"),
    JSON.stringify(
      {
        schema: "atelier-client-browser-review/1",
        status: "failed",
        error: String(error),
        checks,
        screenshots,
        runtimeExceptions: exceptions,
        requestFailures,
        limits: ["Partial capture only; this run did not complete all checks."],
      },
      null,
      2,
    ),
  );
  console.error(String(error));
  process.exitCode = 1;
} finally {
  try {
    await call("Browser.close");
  } catch {}
  browser.kill();
}
