import { baseApi } from "../baseApi";

export const authApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation({
      query: (payload) => ({
        url: "/api/v1/auth/login",
        method: "POST",
        body: payload,
      }),
    }),
    register: builder.mutation({
      query: (payload) => ({
        url: "/api/v1/auth/register",
        method: "POST",
        body: payload,
      }),
    }),
    getPermissions: builder.query({
      query: () => ({ url: "/api/v1/auth/permissions", method: "GET" }),
    }),
    getSessions: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/sessions/",
        method: "GET",
        params,
      }),
      providesTags: ["Sessions"],
    }),
    revokeSession: builder.mutation({
      query: (id) => ({
        url: `/api/v1/sessions/${id}/revoke`,
        method: "POST",
      }),
      invalidatesTags: ["Sessions"],
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useGetPermissionsQuery,
  useGetSessionsQuery,
  useRevokeSessionMutation,
} = authApi;
