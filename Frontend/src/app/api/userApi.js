import { baseApi } from "../baseApi";

export const userApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getUsers: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/users/",
        method: "GET",
        params,
      }),
      providesTags: ["Users"],
    }),
    getUserById: builder.query({
      query: (id) => ({
        url: `/api/v1/users/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Users", id }],
    }),
    createUser: builder.mutation({
      query: (body) => ({
        url: "/api/v1/users/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Users"],
    }),
    updateUser: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/users/${id}`,
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
        url: `/api/v1/users/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Users"],
    }),
    getRoles: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/roles/",
        method: "GET",
        params,
      }),
      providesTags: ["Roles"],
    }),
    getRoleById: builder.query({
      query: (id) => ({
        url: `/api/v1/roles/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Roles", id }],
    }),
    createRole: builder.mutation({
      query: (body) => ({
        url: "/api/v1/roles/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Roles"],
    }),
    updateRole: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/roles/${id}`,
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
        url: `/api/v1/roles/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Roles"],
    }),
  }),
});

export const {
  useGetUsersQuery,
  useGetUserByIdQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useGetRolesQuery,
  useGetRoleByIdQuery,
  useCreateRoleMutation,
  useUpdateRoleMutation,
  useDeleteRoleMutation,
} = userApi;
