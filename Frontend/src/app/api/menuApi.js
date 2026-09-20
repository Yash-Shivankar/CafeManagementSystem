import { baseApi } from "../baseApi";

export const menuApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getMenuCategories: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/menu-categories/",
        method: "GET",
        params,
      }),
      providesTags: ["MenuCategories"],
    }),
    createMenuCategory: builder.mutation({
      query: (body) => ({ url: "/api/v1/menu-categories/", method: "POST", body }),
      invalidatesTags: ["MenuCategories", "MenuItems"],
    }),
    updateMenuCategory: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/menu-categories/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: ["MenuCategories", "MenuItems"],
    }),
    deleteMenuCategory: builder.mutation({
      query: (id) => ({ url: `/api/v1/menu-categories/${id}`, method: "DELETE" }),
      invalidatesTags: ["MenuCategories"],
    }),
    getMenuItems: builder.query({
      query: (params = {}) => ({ url: "/api/v1/menu-items/", method: "GET", params }),
      providesTags: ["MenuItems"],
    }),
    getMenuItemById: builder.query({
      query: (id) => ({ url: `/api/v1/menu-items/${id}`, method: "GET" }),
      providesTags: (result, error, id) => [{ type: "MenuItems", id }],
    }),
    createMenuItem: builder.mutation({
      query: (body) => ({ url: "/api/v1/menu-items/", method: "POST", body }),
      invalidatesTags: ["MenuItems"],
    }),
    updateMenuItem: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/menu-items/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: ["MenuItems"],
    }),
    deleteMenuItem: builder.mutation({
      query: (id) => ({ url: `/api/v1/menu-items/${id}`, method: "DELETE" }),
      invalidatesTags: ["MenuItems"],
    }),
  }),
});

export const {
  useGetMenuCategoriesQuery,
  useCreateMenuCategoryMutation,
  useUpdateMenuCategoryMutation,
  useDeleteMenuCategoryMutation,
  useGetMenuItemsQuery,
  useGetMenuItemByIdQuery,
  useCreateMenuItemMutation,
  useUpdateMenuItemMutation,
  useDeleteMenuItemMutation,
} = menuApi;
