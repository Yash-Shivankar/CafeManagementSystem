const configured = import.meta.env.VITE_BACKEND_URL;

if (!configured && import.meta.env.DEV) {
  console.warn(
    "VITE_BACKEND_URL is not set — calling the API on this origin. " +
      "Set it in Frontend/.env if the backend runs elsewhere (e.g. http://localhost:8000).",
  );
}

export const BaseUrl = (configured || "").replace(/\/+$/, "");

export const APP_BASE = (import.meta.env.BASE_URL || "/").replace(/\/+$/, "") || "";

export const appUrl = (path = "") => `${APP_BASE}/${String(path).replace(/^\/+/, "")}`;

export default BaseUrl;
