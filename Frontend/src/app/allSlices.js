import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { authService } from "../services/auth";

export const allSlices = createApi({
  reducerPath: "allSlices",
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_BACKEND_URL,
    prepareHeaders: (headers) => {
      const token = authService.getToken();

      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  endpoints: (builder) => ({
    login: builder.mutation({
      query: (payload) => ({
        url: "/auth/login/",
        method: "POST",
        body: payload,
      }),
    }),
    getUsers: builder.query({
      query: (params = {}) => ({
        url: "/users/",
        params, // automatically converted to ?key=value
      }),
    }),
  }),
});

export const { useLoginMutation, useGetUsersQuery } = allSlices;
