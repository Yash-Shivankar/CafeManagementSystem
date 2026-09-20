import { authService } from "./auth";

const SELECTED_OUTLET_KEY = "caelum_outlet";

class OutletService {
  constructor() {
    this.listeners = new Set();
  }

  available() {
    return authService.getUser()?.outlets ?? [];
  }

  home() {
    return authService.getUser()?.outlet ?? null;
  }

  selectedId() {
    let stored = null;
    try {
      stored = localStorage.getItem(SELECTED_OUTLET_KEY);
    } catch {
    }

    if (stored) {
      const id = Number(stored);

      if (this.available().some((o) => o.id === id)) return id;
    }

    return this.home()?.id ?? null;
  }

  selected() {
    const id = this.selectedId();
    return this.available().find((o) => o.id === id) ?? this.home();
  }

  canSwitch() {
    return this.available().length > 1;
  }

  select(outletId) {
    try {
      if (outletId == null) {
        localStorage.removeItem(SELECTED_OUTLET_KEY);
      } else {
        localStorage.setItem(SELECTED_OUTLET_KEY, String(outletId));
      }
    } catch {
    }
    this.listeners.forEach((listener) => listener(this.selected()));
  }

  clear() {
    try {
      localStorage.removeItem(SELECTED_OUTLET_KEY);
    } catch {
    }
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
}

export const outletService = new OutletService();
