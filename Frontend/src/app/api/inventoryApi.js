import { baseApi } from "../baseApi";

export const inventoryApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getInventoryCategories: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/inventory-categories/",
        method: "GET",
        params,
      }),
      providesTags: ["InventoryCategories"],
    }),
    getInventoryCategoryById: builder.query({
      query: (id) => ({
        url: `/api/v1/inventory-categories/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [
        { type: "InventoryCategories", id },
      ],
    }),
    createInventoryCategory: builder.mutation({
      query: (body) => ({
        url: "/api/v1/inventory-categories/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["InventoryCategories"],
    }),
    updateInventoryCategory: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/inventory-categories/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "InventoryCategories", id },
        "InventoryCategories",
      ],
    }),
    deleteInventoryCategory: builder.mutation({
      query: (id) => ({
        url: `/api/v1/inventory-categories/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["InventoryCategories"],
    }),
    getInventoryItems: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/inventory-items/",
        method: "GET",
        params,
      }),
      providesTags: ["InventoryItems"],
    }),
    getInventoryItemById: builder.query({
      query: (id) => ({
        url: `/api/v1/inventory-items/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "InventoryItems", id }],
    }),
    createInventoryItem: builder.mutation({
      query: (body) => ({
        url: "/api/v1/inventory-items/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["InventoryItems"],
    }),
    updateInventoryItem: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/inventory-items/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "InventoryItems", id },
        "InventoryItems",
      ],
    }),
    deleteInventoryItem: builder.mutation({
      query: (id) => ({
        url: `/api/v1/inventory-items/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["InventoryItems"],
    }),
    getInventoryLogs: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/inventory-logs/",
        method: "GET",
        params,
      }),
      providesTags: ["InventoryLogs"],
    }),
    createInventoryLog: builder.mutation({
      query: (body) => ({
        url: "/api/v1/inventory-logs/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["InventoryLogs"],
    }),
    getLowStockItems: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/inventory-items/low-stock",
        method: "GET",
        params,
      }),
      providesTags: ["InventoryItems"],
    }),
  }),
});

export const {
  useGetInventoryCategoriesQuery,
  useGetInventoryCategoryByIdQuery,
  useCreateInventoryCategoryMutation,
  useUpdateInventoryCategoryMutation,
  useDeleteInventoryCategoryMutation,
  useGetInventoryItemsQuery,
  useGetInventoryItemByIdQuery,
  useCreateInventoryItemMutation,
  useUpdateInventoryItemMutation,
  useDeleteInventoryItemMutation,
  useGetInventoryLogsQuery,
  useCreateInventoryLogMutation,
  useGetLowStockItemsQuery,
} = inventoryApi;
