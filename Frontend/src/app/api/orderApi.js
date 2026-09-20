import { baseApi } from "../baseApi";

export const orderApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getOrders: builder.query({
      query: (params = {}) => ({ url: "/api/v1/orders/", method: "GET", params }),
      providesTags: ["Orders"],
    }),
    getOrderById: builder.query({
      query: (id) => ({ url: `/api/v1/orders/${id}`, method: "GET" }),
      providesTags: (result, error, id) => [{ type: "Orders", id }],
    }),
    openOrder: builder.mutation({
      query: (body) => ({ url: "/api/v1/orders/", method: "POST", body }),
      invalidatesTags: ["Orders", "Tables"],
    }),
    updateOrder: builder.mutation({
      query: ({ id, ...body }) => ({ url: `/api/v1/orders/${id}`, method: "PUT", body }),
      invalidatesTags: ["Orders"],
    }),
    deleteOrder: builder.mutation({
      query: (id) => ({ url: `/api/v1/orders/${id}`, method: "DELETE" }),
      invalidatesTags: ["Orders", "Tables"],
    }),
    addOrderItem: builder.mutation({
      query: ({ orderId, ...body }) => ({
        url: `/api/v1/orders/${orderId}/items`,
        method: "POST",
        body,
      }),
      invalidatesTags: ["Orders"],
    }),
    updateOrderItem: builder.mutation({
      query: ({ orderId, itemId, ...body }) => ({
        url: `/api/v1/orders/${orderId}/items/${itemId}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: ["Orders"],
    }),
    removeOrderItem: builder.mutation({
      query: ({ orderId, itemId, reason }) => ({
        url: `/api/v1/orders/${orderId}/items/${itemId}`,
        method: "DELETE",
        params: reason ? { reason } : undefined,
      }),
      invalidatesTags: ["Orders", "Kitchen"],
    }),
    setOrderItemStatus: builder.mutation({
      query: ({ orderId, itemId, status, reason }) => ({
        url: `/api/v1/orders/${orderId}/items/${itemId}/status`,
        method: "PATCH",
        body: { status, reason },
      }),
      invalidatesTags: ["Orders", "Kitchen"],
    }),
    confirmOrder: builder.mutation({
      query: (id) => ({ url: `/api/v1/orders/${id}/confirm`, method: "POST" }),
      invalidatesTags: ["Orders", "Kitchen"],
    }),
    billOrder: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/orders/${id}/bill`,
        method: "POST",
        body,
      }),
      invalidatesTags: ["Orders", "Kitchen", "Tables", "CustomerInvoices", "Dashboard"],
    }),
    cancelOrder: builder.mutation({
      query: ({ id, reason }) => ({
        url: `/api/v1/orders/${id}/cancel`,
        method: "POST",
        body: { reason },
      }),
      invalidatesTags: ["Orders", "Kitchen", "Tables"],
    }),
    getKitchenQueue: builder.query({
      query: (params = {}) => ({ url: "/api/v1/kitchen/queue", method: "GET", params }),
      providesTags: ["Kitchen"],
    }),
  }),
});

export const {
  useGetOrdersQuery,
  useGetOrderByIdQuery,
  useOpenOrderMutation,
  useUpdateOrderMutation,
  useDeleteOrderMutation,
  useAddOrderItemMutation,
  useUpdateOrderItemMutation,
  useRemoveOrderItemMutation,
  useSetOrderItemStatusMutation,
  useConfirmOrderMutation,
  useBillOrderMutation,
  useCancelOrderMutation,
  useGetKitchenQueueQuery,
} = orderApi;
