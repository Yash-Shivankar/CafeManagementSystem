import { authService } from "./auth";
import { BaseUrl } from "../config/config";

const cache = new Map();

export const getSignedMediaUrl = async (path) => {
  if (!path) return null;

  const cached = cache.get(path);

  if (cached && cached.expiresAt * 1000 > Date.now() + 15_000) {
    return cached.url;
  }

  const response = await fetch(`${BaseUrl}/api/v1/common/media-url`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${authService.getToken()}`,
    },
    body: JSON.stringify({ path }),
  });

  if (!response.ok) return null;

  const body = await response.json();
  const url = `${BaseUrl}${body.url}`;
  cache.set(path, { url, expiresAt: body.expires_at });
  return url;
};

export const openMedia = async (path) => {
  const url = await getSignedMediaUrl(path);
  if (url) window.open(url, "_blank", "noopener,noreferrer");
};

export const clearMediaUrlCache = () => cache.clear();
