import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, URL } from "node:url";

const src = (p) => fileURLToPath(new URL(`./src/${p}`, import.meta.url));
const landingDir = fileURLToPath(new URL("../landing", import.meta.url));

const APP_BASE = "/app/";

const TYPES = {
  ".html": "text/html",
  ".svg": "image/svg+xml",
  ".css": "text/css",
  ".js": "text/javascript",
  ".xml": "application/xml",
  ".txt": "text/plain",
  ".png": "image/png",
  ".webp": "image/webp",
};

const contentType = (file) => TYPES[path.extname(file)] || "application/octet-stream";

const send = (res, file) => {
  res.setHeader("Content-Type", contentType(file));
  res.end(fs.readFileSync(file));
};

/**
 * Serves ../landing at / during `npm run dev`, so one dev server gives the same
 * front door as production: the marketing page at /, the app at /app.
 * In production nginx does this — see Frontend/nginx.conf.
 */
const landingAtRoot = () => ({
  name: "caelum-landing-at-root",
  configureServer(server) {
    server.middlewares.use((req, res, next) => {
      const url = (req.url || "/").split("?")[0];

      if (url === "/" || url === "/index.html") {
        return send(res, path.join(landingDir, "index.html"));
      }

      if (
        url.startsWith(APP_BASE) ||
        url.startsWith("/@") ||
        url.startsWith("/src/") ||
        url.startsWith("/node_modules/")
      ) {
        return next();
      }

      const candidate = path.join(landingDir, url.replace(/^\/+/, ""));
      if (
        candidate.startsWith(landingDir) &&
        fs.existsSync(candidate) &&
        fs.statSync(candidate).isFile()
      ) {
        return send(res, candidate);
      }

      return next();
    });
  },
});

export default defineConfig({
  base: APP_BASE,
  plugins: [react(), landingAtRoot()],

  resolve: {
    alias: {
      "@": src(""),
      "@app": src("app"),
      "@components": src("components"),
      "@config": src("config"),
      "@pages": src("pages"),
      "@services": src("services"),
      "@utils": src("utils"),
    },
  },

  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          const parts = id.split(/[\\/]node_modules[\\/]/);
          if (parts.length < 2) return undefined;

          const pkg = parts[parts.length - 1].split(/[\\/]/)[0];
          if (
            ["react", "react-dom", "react-router", "react-router-dom", "scheduler"].includes(pkg)
          ) {
            return "react";
          }
          if (["@reduxjs", "react-redux", "redux", "immer", "reselect"].includes(pkg)) {
            return "redux";
          }
          return "vendor";
        },
      },
    },
  },

  test: {
    environment: "node",
    globals: true,
    setupFiles: ["./src/test/setup.js"],
    css: false,
    include: ["src/**/*.{test,spec}.{js,jsx}"],
    testTimeout: 20000,
    hookTimeout: 20000,
  },
});
