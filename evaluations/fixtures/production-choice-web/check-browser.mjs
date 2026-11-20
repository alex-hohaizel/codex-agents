import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, mkdtemp, readdir, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const [binary, outputArgument] = process.argv.slice(2);
assert(binary && outputArgument, "Usage: node check-browser.mjs <Chromium binary> <evidence directory>");
const output = path.resolve(outputArgument);
const masterRoot = path.dirname(fileURLToPath(import.meta.url));
const profile = await mkdtemp(path.join(os.tmpdir(), "atelier-browser-"));
const browser = spawn(binary, ["--headless", "--no-first-run", "--disable-background-networking",
  `--user-data-dir=${profile}`, "--remote-debugging-pipe"], { stdio: ["ignore", "ignore", "inherit", "pipe", "pipe"] });
const browserClosed = new Promise((resolve) => browser.once("close", resolve));
const pending = new Map();
const events = [];
let serial = 0;
let buffer = "";

browser.stdio[4].setEncoding("utf8");
browser.stdio[4].on("data", (chunk) => {
  buffer += chunk;
  const frames = buffer.split("\0");
  buffer = frames.pop();
  for (const frame of frames) {
    const message = JSON.parse(frame);
    const ticket = pending.get(message.id);
    if (!ticket) {
      events.push(message);
      continue;
    }
    clearTimeout(ticket.timer);
    pending.delete(message.id);
    if (message.error) ticket.reject(new Error(message.error.message));
    else ticket.resolve(message.result);
  }
});

function cdp(method, params = {}, sessionId) {
  return new Promise((resolve, reject) => {
    const id = ++serial;
    const timer = setTimeout(() => {
      pending.delete(id);
      reject(new Error(`No Chromium response for ${method}`));
    }, 10000);
    pending.set(id, { resolve, reject, timer });
    browser.stdio[3].write(JSON.stringify({ id, method, params, sessionId }) + "\0");
  });
}

const pause = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const digest = (bytes) => createHash("sha256").update(bytes).digest("hex");
const results = [];
function check(id, condition) {
  assert(condition, id);
  results.push(id);
}

async function page(file, mobile) {
  const { targetId } = await cdp("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await cdp("Target.attachToTarget", { targetId, flatten: true });
  const command = (method, params) => cdp(method, params, sessionId);
  const value = async (expression) => {
    const response = await command("Runtime.evaluate", { expression, returnByValue: true });
    if (response.exceptionDetails) throw new Error(response.exceptionDetails.exception?.description);
    return response.result.value;
  };
  const selector = (css) => `document.querySelector(${JSON.stringify(css)})`;
  const press = async (key) => {
    const windowsVirtualKeyCode = { Enter: 13, Tab: 9 }[key];
    await command("Input.dispatchKeyEvent", { type: "keyDown", key, code: key, windowsVirtualKeyCode,
      ...(key === "Enter" ? { text: "\r", unmodifiedText: "\r", nativeVirtualKeyCode: 36 } : {}) });
    await command("Input.dispatchKeyEvent", { type: "keyUp", key, code: key, windowsVirtualKeyCode });
  };
  const click = async (css) => {
    const point = await value(`(() => {
      const node = ${selector(css)};
      node.scrollIntoView({block: 'center'});
      const rect = node.getBoundingClientRect();
      return {x: (rect.left + rect.right) / 2, y: (rect.top + rect.bottom) / 2};
    })()`);
    if (mobile) {
      await command("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [point] });
      await command("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    } else {
      await command("Input.dispatchMouseEvent", { type: "mousePressed", ...point, button: "left", clickCount: 1 });
      await command("Input.dispatchMouseEvent", { type: "mouseReleased", ...point, button: "left", clickCount: 1 });
    }
  };
  const screenshot = async (name) => {
    const { data } = await command("Page.captureScreenshot", { format: "png" });
    const bytes = Buffer.from(data, "base64");
    await writeFile(path.join(output, name), bytes);
    return { path: name, sha256: digest(bytes) };
  };
  const text = (css) => value(`${selector(css)}.textContent`);
  const waitFor = async (expression) => {
    for (let attempt = 0; attempt < 100; attempt++) {
      if (await value(expression)) return;
      await pause(20);
    }
    throw new Error(`Timed out waiting for browser state: ${expression}`);
  };
  await command("Page.enable");
  await command("Runtime.enable");
  await command("Emulation.setDeviceMetricsOverride", { width: mobile ? 390 : 1440,
    height: mobile ? 844 : 900, deviceScaleFactor: 1, mobile });
  if (mobile) await command("Emulation.setTouchEmulationEnabled", { enabled: true });
  const url = pathToFileURL(path.join(masterRoot, file)).href;
  const navigation = await command("Page.navigate", { url });
  assert(!navigation.errorText, navigation.errorText);
  for (let i = 0; i < 100; i++) {
    if (await value(`location.href === ${JSON.stringify(url)} && document.readyState === 'complete'`)) {
      return { value, click, press, text, screenshot, waitFor, close: () => cdp("Target.closeTarget", { targetId }) };
    }
    await pause(50);
  }
  throw new Error(`Page did not open: ${file}`);
}

async function riverdesk(mobile) {
  const view = await page("riverdesk.html", mobile);
  const label = mobile ? "phone" : "desktop";
  await view.value("localStorage.clear()");
  await view.click("#reports li:nth-child(2) button");
  check(`${label} queue item selected`, await view.text("#report-id") === "LF-042");
  check(`${label} source review is required`, await view.value("document.querySelector('#handoff').disabled"));
  if (mobile) await view.click("#evidence summary");
  else {
    await view.value("document.querySelector('#reports li:nth-child(3) button').focus()");
    await view.press("Tab");
    check("desktop keyboard reaches source summary", await view.value("document.activeElement.tagName === 'SUMMARY'"));
    await view.press("Enter");
  }
  check(`${label} evidence actually open`, await view.value("document.querySelector('#evidence').open"));
  check(`${label} selected provenance`, await view.text("#source") === "Duty keeper's field notes");
  const shot = await view.screenshot(`riverdesk-${label}.png`);
  await view.value(`document.querySelector('#role').value = 'viewer'; document.querySelector('#role').dispatchEvent(new Event('change'))`);
  check(`${label} viewer reads evidence and cannot hand off`, await view.value("document.querySelector('#handoff').hidden && document.querySelector('#handoff').disabled && document.querySelector('#evidence').open"));
  await view.value(`document.querySelector('#role').value = 'operator'; document.querySelector('#role').dispatchEvent(new Event('change')); localStorage.setItem('riverdesk-revision:LF-042', '2')`);
  await view.click("#handoff");
  check(`${label} conflict keeps selected report`, (await view.text("#status")).startsWith("LF-042 changed") &&
    await view.value("!refresh.hidden && handoff.disabled && localStorage.getItem('riverdesk-handoff:LF-042') === null"));
  await view.click("#refresh");
  check(`${label} refresh requires fresh review`, (await view.text("#status")).startsWith("Loaded revision 2") &&
    await view.value("handoff.disabled && document.activeElement.tagName === 'SUMMARY'"));
  await view.click("#evidence summary");
  await view.waitFor("!document.querySelector('#handoff').disabled");
  await view.click("#handoff");
  check(`${label} actual browser receipt targets exact report and revision`, await view.value(
    "localStorage.getItem('riverdesk-handoff:LF-042') === 'Duty review received LF-042, revision 2.'"));
  check(`${label} layout fits viewport`, await view.value("document.documentElement.scrollWidth === innerWidth"));
  if (mobile) check("phone stacks evidence after queue", await view.value(
    "document.querySelector('.detail').getBoundingClientRect().top >= document.querySelector('.queue').getBoundingClientRect().bottom"));
  else check("desktop keeps evidence beside queue", await view.value(
    "document.querySelector('.detail').getBoundingClientRect().top === document.querySelector('.queue').getBoundingClientRect().top"));
  await view.close();
  return shot;
}

async function riverlines(mobile) {
  const view = await page("riverlines.html", mobile);
  const label = mobile ? "phone" : "desktop";
  check(`${label} editorial lead`, (await view.text("h1")).replace(/\s/g, "") === "Followthewater.");
  const shot = await view.screenshot(`riverlines-${label}.png`);
  await view.click("#chronology li:nth-child(2) a");
  check(`${label} chronology changes article and focus`, await view.value(
    "document.activeElement.id === 'story-title' && document.querySelector('[aria-current]').textContent === '02 / Old mill'"));
  check(`${label} same scenario has editorial account`, await view.text("#story-title") === "The mill gate remains open");
  await view.click("#notes summary");
  check(`${label} press opens article specific source`, (await view.text("#story-source")).includes("Duty keeper's field notes") &&
    await view.value("document.querySelector('#notes').open && document.querySelector('#handoff') === null"));
  check(`${label} editorial layout fits viewport`, await view.value("document.documentElement.scrollWidth === innerWidth"));
  await view.close();
  return shot;
}

try {
  await mkdir(output, { recursive: true });
  const { product, userAgent } = await cdp("Browser.getVersion");
  const screenshots = [];
  for (const mobile of [false, true]) screenshots.push(await riverdesk(mobile), await riverlines(mobile));
  check("no uncaught JavaScript errors", !events.some(({ method }) => method === "Runtime.exceptionThrown"));
  const files = (await readdir(masterRoot)).filter((name) => /\.(html|css|js|md|mjs)$/.test(name)).sort();
  const sources = await Promise.all(files.map(async (name) => ({ path: name, sha256: digest(await readFile(path.join(masterRoot, name))) })));
  const receipt = { product, userAgent, method: "browser", input: ["1440×900 mouse and keyboard", "390×844 touch emulation"],
    scope: "local browser with synthetic data and localStorage; no physical device, server permission, or human acceptance claim",
    checks: results, screenshots, sources };
  await writeFile(path.join(output, "browser-receipt.json"), JSON.stringify(receipt, null, 2) + "\n");
  console.log(`${product}: ${results.length} assertions; ${output}`);
} finally {
  browser.kill();
  await browserClosed;
  await rm(profile, { recursive: true, force: true });
}
