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

    getSettings: builder.query({
      query: (params = {}) => ({
        url: "/settings/",
        method: "GET",
        params,
      }),
      providesTags: ["Settings"],
    }),
    getSettingById: builder.query({
      query: (id) => ({
        url: `/settings/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Settings", id }],
    }),
    createSetting: builder.mutation({
      query: (body) => ({
        url: "/settings/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Settings"],
    }),
    updateSetting: builder.mutation({
      query: ({ key, value }) => ({
        url: `/settings/${key}`,
        method: "PUT",
        body: { value },
      }),
      invalidatesTags: (result, error, { key }) => [
        { type: "Settings", id: key },
        "Settings",
      ],
    }),
    deleteSetting: builder.mutation({
      query: (id) => ({
        url: `/settings/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Settings"],
    }),

    getUsers: builder.query({
      query: (params = {}) => ({
        url: "/users/",
        method: "GET",
        params,
      }),
      providesTags: ["Users"],
    }),
    getUserById: builder.query({
      query: (id) => ({
        url: `/users/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Users", id }],
    }),
    createUser: builder.mutation({
      query: (body) => ({
        url: "/users/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Users"],
    }),
    updateUser: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/users/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Users", id },
        "Users",
      ],
    }),
    deleteUser: builder.mutation({
      query: (id) => ({
        url: `/users/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Users"],
    }),

    getRoles: builder.query({
      query: (params = {}) => ({
        url: "/roles/",
        method: "GET",
        params,
      }),
      providesTags: ["Roles"],
    }),
    getRoleById: builder.query({
      query: (id) => ({
        url: `/roles/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Roles", id }],
    }),
    createRole: builder.mutation({
      query: (body) => ({
        url: "/roles/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Roles"],
    }),
    updateRole: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/roles/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Roles", id },
        "Roles",
      ],
    }),
    deleteRole: builder.mutation({
      query: (id) => ({
        url: `/roles/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Roles"],
    }),
  }),
});

export const {
  useLoginMutation,

  // Settings
  useGetSettingsQuery,
  useGetSettingByIdQuery,
  useCreateSettingMutation,
  useUpdateSettingMutation,
  useDeleteSettingMutation,

  // Users
  useGetUsersQuery,
  useGetUserByIdQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,

  // Roles
  useGetRolesQuery,
  useGetRoleByIdQuery,
  useCreateRoleMutation,
  useUpdateRoleMutation,
  useDeleteRoleMutation,
} = allSlices;
