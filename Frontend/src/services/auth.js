import { CRUD } from "../config/permissions";

class AuthService {
  constructor() {
    this.token = localStorage.getItem("auth_token");
    this.user = JSON.parse(localStorage.getItem("auth_user") || "null");
  }

  setAuth(data) {
    this.token = data.access_token;

    this.user = {
      ...data.user,
      permissions: {
        dashboard: [...CRUD],
        users: [...CRUD],
        settings: [...CRUD],
      },
    };

    localStorage.setItem("auth_token", data.access_token);
    localStorage.setItem("auth_user", JSON.stringify(this.user));
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem("auth_token", token);
  }

  getToken() {
    return this.token || localStorage.getItem("auth_token");
  }

  getUser() {
    return this.user || JSON.parse(localStorage.getItem("auth_user"));
  }

  hasPermission(module, action) {
    return this.getUser()?.permissions?.[module]?.includes(action);
  }

  logout() {
    localStorage.clear();
    window.location.href = "/login";
  }
}

export const authService = new AuthService();
