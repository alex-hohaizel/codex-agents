import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const [binary, destination] = process.argv.slice(2);
assert(binary && destination, "Use: node check-game.mjs <Chromium executable> <new output directory>");
const output = path.resolve(destination);
const root = path.dirname(fileURLToPath(import.meta.url));
const temp = await mkdtemp(path.join(tmpdir(), "tram-probe-"));
const files = ["index.html", "mesh.js", "tram.js", "tram.css"];
const digest = (bytes) => createHash("sha256").update(bytes).digest("hex");
const source = async (name) => {
  const bytes = await readFile(path.join(root, name));
  return { bytes, pin: { path: name, sha256: digest(bytes), bytes: bytes.length } };
};
const browser = spawn(binary, ["--headless", "--no-first-run", "--disable-background-networking",
  "--enable-unsafe-swiftshader", `--user-data-dir=${path.join(temp, "profile")}`, "--remote-debugging-pipe"],
{ stdio: ["ignore", "ignore", "inherit", "pipe", "pipe"] });
const closed = new Promise((resolve) => browser.once("close", resolve));
const pending = new Map();
let serial = 0;
let partial = "";
browser.stdio[4].setEncoding("utf8");
browser.stdio[4].on("data", (chunk) => {
  const lines = (partial + chunk).split("\0");
  partial = lines.pop();
  for (const line of lines) {
    const message = JSON.parse(line);
    const callback = pending.get(message.id);
    if (callback) callback(message);
  }
});

function send(method, params = {}, sessionId) {
  return new Promise((resolve, reject) => {
    const id = ++serial;
    const timer = setTimeout(() => reject(new Error(`No browser response for ${method}`)), 12000);
    pending.set(id, ({ result, error }) => {
      clearTimeout(timer);
      pending.delete(id);
      if (error) reject(new Error(error.message));
      else resolve(result);
    });
    browser.stdio[3].write(JSON.stringify({ id, method, params, sessionId }) + "\0");
  });
}

try {
  await mkdir(output, { recursive: false });
  const { product } = await send("Browser.getVersion");
  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  const page = (method, params) => send(method, params, sessionId);
  await page("Page.enable");
  await page("Emulation.setDeviceMetricsOverride", { width: 1220, height: 900, deviceScaleFactor: 1, mobile: false });
  const value = async (expression) => {
    const reply = await page("Runtime.evaluate", { expression, returnByValue: true });
    if (reply.exceptionDetails) throw new Error(reply.exceptionDetails.exception?.description);
    return reply.result.value;
  };
  const waitFor = async (expression) => {
    for (let attempt = 0; attempt < 100; attempt++) {
      if (await value(expression)) return;
      await new Promise((resolve) => setTimeout(resolve, 30));
    }
    throw new Error(`No observed state: ${expression}`);
  };
  const open = async (file) => {
    const url = pathToFileURL(file).href;
    assert(!(await page("Page.navigate", { url })).errorText, "Browser could not open scenario");
    await waitFor(`location.href === ${JSON.stringify(url)} && document.readyState === 'complete'`);
  };
  const key = async (key) => {
    const codes = { Enter: 13, ArrowRight: 39 };
    const input = { key, code: key, windowsVirtualKeyCode: codes[key] };
    await page("Input.dispatchKeyEvent", { ...input, type: "rawKeyDown" });
    await page("Input.dispatchKeyEvent", { ...input, type: "keyUp" });
  };
  const screenshot = async (name) => {
    const { data } = await page("Page.captureScreenshot", { format: "png" });
    const bytes = Buffer.from(data, "base64");
    await writeFile(path.join(output, name), bytes);
    return { path: name, sha256: digest(bytes) };
  };
  const status = (text) => value(`document.querySelector('#status').textContent.includes(${JSON.stringify(text)})`);
  await open(path.join(root, "index.html"));
  const importState = await value("({...document.querySelector('canvas').dataset})");
  assert.equal(importState.triangles, "6", "Editable 3D asset was imported and drawn");
  assert(importState.renderer, "The actual renderer must be observed");
  const framebuffer = async () => digest(await value("document.querySelector('canvas').toDataURL('image/png')"));
  const startingFrame = await framebuffer();
  const before = await screenshot("before-docking.png");
  await key("Enter");
  assert(await status("Move to the green marker"), "Early docking is refused");
  for (let step = 1; step < 5; step++) await key("ArrowRight");
  assert(await status("Position 5 of 5"), "Four keyboard movements advance four positions");
  await key("Enter");
  assert(await status("Trolley secured"), "Docking succeeds only when aligned");
  const warmDraw = Number(await value("document.querySelector('canvas').dataset.drawMs"));
  assert(warmDraw < 150, "Warmed frame exceeded the 150 ms budget");
  const after = await screenshot("after-docking.png");
  const dockedFrame = await framebuffer();
  assert.notEqual(dockedFrame, startingFrame, "The actual WebGL frame responds to the control");
  await page("Page.reload");
  await waitFor("document.querySelector('#status')?.textContent.includes('Trolley restored to Dock 04')");

  const broken = path.join(temp, "broken-asset");
  await mkdir(broken);
  for (const name of files) {
    const { bytes } = await source(name);
    const data = name === "mesh.js" ? bytes.toString().replace("[4, 5, 6", "[99, 5, 6") : bytes;
    await writeFile(path.join(broken, name), data);
  }
  await open(path.join(broken, "index.html"));
  assert(await status("Invalid deck face indices"), "Broken mesh is refused by the consumer");
  assert(await value("document.querySelector('#reset').disabled"), "An invalid import keeps controls disabled");
  const rejection = await value("document.querySelector('#status').textContent");
  const sources = await Promise.all([...files, "README.md", "check-game.mjs"].map(async (name) => (await source(name)).pin));
  const runtimeBytes = sources.slice(0, files.length).reduce((total, pin) => total + pin.bytes, 0);
  assert(runtimeBytes < 20 * 1024, "Original scene and runtime exceed the size budget");
  const receipt = { method: "runtime", environment: product, matrix: "Desktop 1220×900 / keyboard / local Chromium WebGL",
    renderer: importState.renderer, triangles: Number(importState.triangles), warmDrawMs: warmDraw, runtimeBytes, sources,
    screenshots: [before, after], canvasPngDataUrlSha256: { startingFrame, dockedFrame },
    positive: "Keyboard traversal, gated docking, changed WebGL frame and persisted reload verified",
    negative: rejection, scope: "Browser-target synthetic 3D interaction. Does not exercise native iOS/Android or a hardware matrix." };
  await writeFile(path.join(output, "game-receipt.json"), JSON.stringify(receipt, null, 2) + "\n");
  console.log(JSON.stringify(receipt, null, 2));
} finally {
  browser.kill();
  await closed;
  await rm(temp, { recursive: true, force: true });
}
