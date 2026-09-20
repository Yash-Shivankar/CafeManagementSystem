import { BaseUrl, appUrl } from "../config/config";
import { sessionEnded, sessionStarted, bootstrapSettled } from "../app/authSlice";

const USER_CACHE_KEY = "caelum_user";

class AuthService {
  constructor() {
    this.token = null;
    this.tokenExpiresAt = 0;
    this.user = this._readCachedUser();
    this.store = null;
    this.listeners = new Set();
  }

  bindStore(store) {
    this.store = store;
    if (this.user) store.dispatch(sessionStarted(this.user));

    if (typeof window !== "undefined") {
      window.addEventListener("storage", (event) => {
        if (event.key !== USER_CACHE_KEY) return;

        this.user = this._readCachedUser();
        if (this.user) {
          this.store?.dispatch(sessionStarted(this.user));
        } else {
          this.token = null;
          this.tokenExpiresAt = 0;
          this.store?.dispatch(sessionEnded());
        }
        this._notify();
      });
    }
  }

  _readCachedUser() {
    try {
      return JSON.parse(localStorage.getItem(USER_CACHE_KEY) || "null");
    } catch {
      return null;
    }
  }

  _writeCachedUser(user) {
    try {
      if (user) {
        localStorage.setItem(USER_CACHE_KEY, JSON.stringify(user));
      } else {
        localStorage.removeItem(USER_CACHE_KEY);
      }
    } catch {
    }
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  _notify() {
    this.listeners.forEach((listener) => listener(this.user));
  }

  setAuth(data) {
    this.token = data.access_token;
    this.tokenExpiresAt = Date.now() + (data.expires_in ?? 3600) * 1000;
    this.user = data.user ?? null;
    this._writeCachedUser(this.user);
    this.store?.dispatch(sessionStarted(this.user));
    this._notify();
  }

  getToken() {
    return this.token;
  }

  getUser() {
    return this.user;
  }

  isAuthenticated() {
    return Boolean(this.token);
  }

  needsRefresh() {
    return !this.token || Date.now() > this.tokenExpiresAt - 30_000;
  }

  async bootstrap() {
    try {
      const response = await fetch(`${BaseUrl}/api/v1/auth/refresh`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        this.clear();
        return false;
      }

      this.setAuth(await response.json());
      return true;
    } catch {
      this.clear();
      return false;
    } finally {
      this.store?.dispatch(bootstrapSettled());
    }
  }

  hasPermission(module, action) {
    const permissions = this.user?.permissions?.[module];
    return Array.isArray(permissions) && permissions.includes(action);
  }

  canView(module) {
    return this.hasPermission(module, "view");
  }

  clear() {
    this.token = null;
    this.tokenExpiresAt = 0;
    this.user = null;
    this._writeCachedUser(null);
    try {
      localStorage.removeItem("caelum_outlet");
    } catch {
    }
    this.store?.dispatch(sessionEnded());
    this._notify();
  }

  async logout() {
    try {
      await fetch(`${BaseUrl}/api/v1/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch {
    }
    this.clear();
    window.location.href = appUrl("login");
  }
}

export const authService = new AuthService();
