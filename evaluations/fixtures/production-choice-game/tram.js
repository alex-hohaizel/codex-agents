"use strict";

const status = document.getElementById("status");
const canvas = document.querySelector("canvas");
const reset = document.getElementById("reset");
const stateKey = "fen-tram.progress.v1";
const docks = [-0.65, -0.33, 0, 0.33, 0.65];
let position = 0;
let docked = false;

function importDeck(mesh) {
  if (mesh.format !== "atelier.mesh/1" || !mesh.vertices.every((point) =>
    point.length === 3 && point.every(Number.isFinite))) throw new Error("Unreadable deck geometry");
  return mesh.surfaces.map(({ indices, color }) => {
    if (!indices.length || indices.length % 3 !== 0 || !indices.every((index) =>
      Number.isInteger(index) && index >= 0 && index < mesh.vertices.length)) throw new Error("Invalid deck face indices");
    return { vertices: indices.flatMap((index) => mesh.vertices[index]), color };
  });
}

function model() {
  const deck = importDeck(tramDeck);
  const gl = canvas.getContext("webgl", { preserveDrawingBuffer: true, antialias: false });
  if (!gl) throw new Error("WebGL graphics context unavailable");
  const compile = (type, source) => {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader));
    return shader;
  };
  const program = gl.createProgram();
  gl.attachShader(program, compile(gl.VERTEX_SHADER, `
    attribute vec3 point;
    void main() {
      gl_Position = vec4(point.x * .85 + point.z * .40, point.y * 1.1 - point.z * .68 + point.x * .20, .6 - point.y * .54 - point.z * .60, 1.0);
    }`));
  gl.attachShader(program, compile(gl.FRAGMENT_SHADER, `
    precision mediump float;
    uniform vec3 shade;
    void main() { gl_FragColor = vec4(shade, 1.0); }
  `));
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
  gl.useProgram(program);
  const point = gl.getAttribLocation(program, "point");
  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.enableVertexAttribArray(point);
  gl.vertexAttribPointer(point, 3, gl.FLOAT, false, 0, 0);
  gl.enable(gl.DEPTH_TEST);
  gl.clearColor(0.08, 0.14, 0.16, 1);
  const shade = gl.getUniformLocation(program, "shade");
  const draw = ({ vertices, color }) => {
    gl.uniform3fv(shade, color);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STREAM_DRAW);
    gl.drawArrays(gl.TRIANGLES, 0, vertices.length / 3);
  };
  const slab = (x, y, width, length, color) => ({ color, vertices: [
    x - width, y, -length, x + width, y, -length, x + width, y, length,
    x - width, y, -length, x + width, y, length, x - width, y, length,
  ] });
  const graphics = gl.getExtension("WEBGL_debug_renderer_info");
  canvas.dataset.renderer = graphics ? gl.getParameter(graphics.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
  canvas.dataset.triangles = deck.reduce((total, face) => total + face.vertices.length / 9, 0);
  return () => {
    const start = performance.now();
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    deck.forEach(draw);
    draw(slab(docks[4], 0.02, .11, .27, [0.57, .89, .51]));
    draw(slab(docks[position], 0.10, .09, .13, docked ? [0.74, 1, 0.5] : [1, .65, .24]));
    gl.finish();
    canvas.dataset.drawMs = performance.now() - start;
  };
}

reset.disabled = true;
try {
  const draw = model();
  function commit(message) {
    localStorage.setItem(stateKey, JSON.stringify({ position, docked }));
    status.textContent = message;
    draw();
  }
  const saved = JSON.parse(localStorage.getItem(stateKey) || "null");
  if (saved && Number.isInteger(saved.position) && saved.position in docks && typeof saved.docked === "boolean") {
    ({ position, docked } = saved);
  }
  draw();
  status.textContent = docked ? "Trolley restored to Dock 04." : `Position ${position + 1} of ${docks.length}.`;
  reset.disabled = false;
  reset.addEventListener("click", () => {
    position = 0;
    docked = false;
    commit("Trolley returned to the starting siding.");
  });
  document.addEventListener("keydown", (event) => {
    if (event.target === reset || !["ArrowLeft", "ArrowRight", "Enter"].includes(event.key)) return;
    event.preventDefault();
    if (event.key === "Enter") {
      docked = position === docks.length - 1;
      commit(docked ? "Trolley secured at Dock 04." : "Move to the green marker before docking.");
    } else if (!docked) {
      const direction = event.key === "ArrowRight" ? 1 : -1;
      position = Math.max(0, Math.min(docks.length - 1, position + direction));
      commit(`Position ${position + 1} of ${docks.length}.`);
    }
  });
} catch (error) {
  status.textContent = `Tram unavailable. ${error.message}.`;
}
