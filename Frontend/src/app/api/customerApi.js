import { baseApi } from "../baseApi";

export const customerApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getCustomerFeedbacks: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/customer-feedbacks/",
        method: "GET",
        params,
      }),
      providesTags: ["CustomerFeedbacks"],
    }),
    getCustomerFeedbackById: builder.query({
      query: (id) => ({
        url: `/api/v1/customer-feedbacks/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "CustomerFeedbacks", id }],
    }),
    createCustomerFeedback: builder.mutation({
      query: (body) => ({
        url: "/api/v1/customer-feedbacks/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["CustomerFeedbacks"],
    }),
    updateCustomerFeedback: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/customer-feedbacks/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "CustomerFeedbacks", id },
        "CustomerFeedbacks",
      ],
    }),
    deleteCustomerFeedback: builder.mutation({
      query: (id) => ({
        url: `/api/v1/customer-feedbacks/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["CustomerFeedbacks"],
    }),
    getCustomerInvoices: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/customer-invoices/",
        method: "GET",
        params,
      }),
      providesTags: ["CustomerInvoices"],
    }),
    getCustomerInvoiceById: builder.query({
      query: (id) => ({
        url: `/api/v1/customer-invoices/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "CustomerInvoices", id }],
    }),
    createCustomerInvoice: builder.mutation({
      query: (body) => ({
        url: "/api/v1/customer-invoices/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["CustomerInvoices"],
    }),
    updateCustomerInvoice: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/customer-invoices/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "CustomerInvoices", id },
        "CustomerInvoices",
      ],
    }),
    deleteCustomerInvoice: builder.mutation({
      query: (id) => ({
        url: `/api/v1/customer-invoices/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["CustomerInvoices"],
    }),
    getServices: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/services/",
        method: "GET",
        params,
      }),
      providesTags: ["Services"],
    }),
    getServiceById: builder.query({
      query: (id) => ({
        url: `/api/v1/services/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Services", id }],
    }),
    createService: builder.mutation({
      query: (body) => ({
        url: "/api/v1/services/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Services"],
    }),
    updateService: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/services/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Services", id },
        "Services",
      ],
    }),
    deleteService: builder.mutation({
      query: (id) => ({
        url: `/api/v1/services/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Services"],
    }),
    getTables: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/tables/",
        method: "GET",
        params,
      }),
      providesTags: ["Tables"],
    }),
    getTableById: builder.query({
      query: (id) => ({
        url: `/api/v1/tables/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Tables", id }],
    }),
    createTable: builder.mutation({
      query: (body) => ({
        url: "/api/v1/tables/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Tables"],
    }),
    updateTable: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/tables/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Tables", id },
        "Tables",
      ],
    }),
    deleteTable: builder.mutation({
      query: (id) => ({
        url: `/api/v1/tables/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Tables"],
    }),
    getBookings: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/bookings/",
        method: "GET",
        params,
      }),
      providesTags: ["Bookings"],
    }),
    getBookingById: builder.query({
      query: (id) => ({
        url: `/api/v1/bookings/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Bookings", id }],
    }),
    createBooking: builder.mutation({
      query: (body) => ({
        url: "/api/v1/bookings/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Bookings"],
    }),
    updateBooking: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/bookings/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Bookings", id },
        "Bookings",
      ],
    }),
    deleteBooking: builder.mutation({
      query: (id) => ({
        url: `/api/v1/bookings/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Bookings"],
    }),
  }),
});

export const {
  useGetCustomerFeedbacksQuery,
  useGetCustomerFeedbackByIdQuery,
  useCreateCustomerFeedbackMutation,
  useUpdateCustomerFeedbackMutation,
  useDeleteCustomerFeedbackMutation,
  useGetCustomerInvoicesQuery,
  useGetCustomerInvoiceByIdQuery,
  useCreateCustomerInvoiceMutation,
  useUpdateCustomerInvoiceMutation,
  useDeleteCustomerInvoiceMutation,
  useGetServicesQuery,
  useGetServiceByIdQuery,
  useCreateServiceMutation,
  useUpdateServiceMutation,
  useDeleteServiceMutation,
  useGetTablesQuery,
  useGetTableByIdQuery,
  useCreateTableMutation,
  useUpdateTableMutation,
  useDeleteTableMutation,
  useGetBookingsQuery,
  useGetBookingByIdQuery,
  useCreateBookingMutation,
  useUpdateBookingMutation,
  useDeleteBookingMutation,
} = customerApi;
