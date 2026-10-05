import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  testMatch: "demo-recording.spec.ts",
  timeout: 240_000,
  workers: 1,
  retries: 0,
  reporter: "list",
  outputDir: "../artifacts/pw-output",
  use: { baseURL: process.env.DEMO_URL ?? "http://127.0.0.1:3000" },
});
