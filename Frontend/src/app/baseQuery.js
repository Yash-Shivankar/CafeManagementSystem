import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { authService } from "../services/auth";
import { outletService } from "../services/outlet";
import { BaseUrl, appUrl } from "../config/config";

const rawBaseQuery = fetchBaseQuery({
  baseUrl: BaseUrl,
  credentials: "include",
  prepareHeaders: (headers) => {
    const token = authService.getToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const outletId = outletService.selectedId();
    if (outletId != null) {
      headers.set("X-Outlet-Id", String(outletId));
    }

    return headers;
  },
});

let refreshPromise = null;

export const baseQueryWithReauth = async (args, api, extraOptions) => {
  let result = await rawBaseQuery(args, api, extraOptions);

  if (result.error?.status === 401) {
    if (!refreshPromise) {
      refreshPromise = authService.bootstrap().finally(() => {
        refreshPromise = null;
      });
    }

    const refreshed = await refreshPromise;

    if (refreshed) {
      result = await rawBaseQuery(args, api, extraOptions);
    } else {
      authService.clear();
      outletService.clear();
      const login = appUrl("login");
      if (window.location.pathname !== login) {
        window.location.href = login;
      }
    }
  }

  return result;
};
