// Records the 30-second opening (demo/intro.html) with neural narration.
//   node record-intro.mjs   → ../artifacts/intro.mp4   (needs `scripts/narration.py prep` first)
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const here = path.dirname(fileURLToPath(import.meta.url));
const ART = path.resolve(here, "../artifacts");
const AUD = path.join(ART, "narration");
const LENGTH = 30;
const CUES = [["i1", 0.4], ["i2", 10.2], ["i3", 20.2]];
const run = (c, a) => execFileSync(c, a, { stdio: ["ignore", "pipe", "pipe"] }).toString();
const clip = (id) => [".wav", ".aiff"].map((e) => path.join(AUD, id + e)).find(fs.existsSync);
const manifest = JSON.parse(fs.readFileSync(path.join(AUD, "manifest.json"), "utf8"));
for (const [id, at] of CUES) if (at + manifest[id] > at + 9.7) console.warn(`${id} is ${manifest[id]}s — longer than its 10s scene`);

const tmp = path.join(ART, "intro-raw");
fs.mkdirSync(tmp, { recursive: true });
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, recordVideo: { dir: tmp, size: { width: 1280, height: 800 } } });
const page = await ctx.newPage();
const t0 = Date.now();
await page.goto("file://" + path.join(here, "intro.html"));
const lead = (Date.now() - t0) / 1000 - 0.1; // the page clock starts when the page loads
await page.waitForTimeout((LENGTH + 0.5) * 1000);
if (process.env.SHOTS) for (const s of process.env.SHOTS.split(",")) { /* handled below via ffmpeg */ }
const raw = await page.video().path();
await ctx.close(); await browser.close();

const inputs = ["-i", raw, ...CUES.flatMap(([id]) => ["-i", clip(id)])];
const mix = CUES.map(([, at], i) => `[${i + 1}:a]aresample=44100,adelay=${Math.round(at * 1000)}:all=1[a${i}]`).join(";")
  + `;${CUES.map((_, i) => `[a${i}]`).join("")}amix=inputs=${CUES.length}:normalize=0[a]`;
const out = path.join(ART, "intro.mp4");
run("ffmpeg", ["-y", ...inputs, "-filter_complex", `[0:v]trim=start=${lead.toFixed(3)}:duration=${LENGTH},setpts=PTS-STARTPTS,fps=30[v];${mix}`,
  "-map", "[v]", "-map", "[a]", "-t", String(LENGTH), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
  "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", "-movflags", "+faststart", out]);
fs.rmSync(tmp, { recursive: true, force: true });
console.log("wrote", out);
