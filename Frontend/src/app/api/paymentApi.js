import { baseApi } from "../baseApi";

export const paymentApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getPayments: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/payments/",
        method: "GET",
        params,
      }),
      providesTags: ["Payments"],
    }),
    getPaymentById: builder.query({
      query: (id) => ({
        url: `/api/v1/payments/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Payments", id }],
    }),
    createPayment: builder.mutation({
      query: (body) => ({
        url: "/api/v1/payments/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Payments"],
    }),
    updatePayment: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/payments/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Payments", id },
        "Payments",
      ],
    }),
    deletePayment: builder.mutation({
      query: (id) => ({
        url: `/api/v1/payments/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Payments"],
    }),
    getEarnings: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/profit-loss/",
        method: "GET",
        params,
      }),
      providesTags: ["Earning"],
    }),
    getEarningById: builder.query({
      query: (id) => ({
        url: `/api/v1/profit-loss/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Earning", id }],
    }),
    createEarning: builder.mutation({
      query: (body) => ({
        url: "/api/v1/profit-loss/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Earning"],
    }),
    updateEarning: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/profit-loss/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Earning", id },
        "Earning",
      ],
    }),
    deleteEarning: builder.mutation({
      query: (id) => ({
        url: `/api/v1/profit-loss/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Earning"],
    }),
  }),
});

export const {
  useGetPaymentsQuery,
  useGetPaymentByIdQuery,
  useCreatePaymentMutation,
  useUpdatePaymentMutation,
  useDeletePaymentMutation,
  useGetEarningsQuery,
  useGetEarningByIdQuery,
  useCreateEarningMutation,
  useUpdateEarningMutation,
  useDeleteEarningMutation,
} = paymentApi;
