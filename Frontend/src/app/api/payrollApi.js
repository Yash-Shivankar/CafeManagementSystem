import { baseApi } from "../baseApi";

export const payrollApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    previewPayroll: builder.mutation({
      query: (body) => ({
        url: "/api/v1/salary-payments/preview",
        method: "POST",
        body,
      }),
    }),
    generatePayroll: builder.mutation({
      query: (body) => ({
        url: "/api/v1/salary-payments/generate",
        method: "POST",
        body,
      }),
      invalidatesTags: ["SalaryPayments", "AuditLogs"],
    }),
    getIncentives: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/incentives/",
        method: "GET",
        params,
      }),
      providesTags: ["Incentives"],
    }),
    getIncentiveById: builder.query({
      query: (id) => ({
        url: `/api/v1/incentives/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Incentives", id }],
    }),
    createIncentive: builder.mutation({
      query: (body) => ({
        url: "/api/v1/incentives/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Incentives"],
    }),
    updateIncentive: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/incentives/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Incentives", id },
        "Incentives",
      ],
    }),
    deleteIncentive: builder.mutation({
      query: (id) => ({
        url: `/api/v1/incentives/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Incentives"],
    }),
    getIncrementHistories: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/increment-histories/",
        method: "GET",
        params,
      }),
      providesTags: ["IncrementHistories"],
    }),
    getIncrementHistoryById: builder.query({
      query: (id) => ({
        url: `/api/v1/increment-histories/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "IncrementHistories", id }],
    }),
    createIncrementHistory: builder.mutation({
      query: (body) => ({
        url: "/api/v1/increment-histories/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["IncrementHistories"],
    }),
    updateIncrementHistory: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/increment-histories/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "IncrementHistories", id },
        "IncrementHistories",
      ],
    }),
    deleteIncrementHistory: builder.mutation({
      query: (id) => ({
        url: `/api/v1/increment-histories/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["IncrementHistories"],
    }),
    getSalaryPayments: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/salary-payments/",
        method: "GET",
        params,
      }),
      providesTags: ["SalaryPayments"],
    }),
    getSalaryPaymentById: builder.query({
      query: (id) => ({
        url: `/api/v1/salary-payments/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "SalaryPayments", id }],
    }),
    createSalaryPayment: builder.mutation({
      query: (body) => ({
        url: "/api/v1/salary-payments/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["SalaryPayments"],
    }),
    updateSalaryPayment: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/salary-payments/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "SalaryPayments", id },
        "SalaryPayments",
      ],
    }),
    deleteSalaryPayment: builder.mutation({
      query: (id) => ({
        url: `/api/v1/salary-payments/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["SalaryPayments"],
    }),
    getSalaryStructures: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/salary-structures/",
        method: "GET",
        params,
      }),
      providesTags: ["SalaryStructures"],
    }),
    getSalaryStructureById: builder.query({
      query: (id) => ({
        url: `/api/v1/salary-structures/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "SalaryStructures", id }],
    }),
    createSalaryStructure: builder.mutation({
      query: (body) => ({
        url: "/api/v1/salary-structures/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["SalaryStructures"],
    }),
    updateSalaryStructure: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/salary-structures/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "SalaryStructures", id },
        "SalaryStructures",
      ],
    }),
    deleteSalaryStructure: builder.mutation({
      query: (id) => ({
        url: `/api/v1/salary-structures/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["SalaryStructures"],
    }),
  }),
});

export const {
  usePreviewPayrollMutation,
  useGeneratePayrollMutation,
  useGetIncentivesQuery,
  useGetIncentiveByIdQuery,
  useCreateIncentiveMutation,
  useUpdateIncentiveMutation,
  useDeleteIncentiveMutation,
  useGetIncrementHistoriesQuery,
  useGetIncrementHistoryByIdQuery,
  useCreateIncrementHistoryMutation,
  useUpdateIncrementHistoryMutation,
  useDeleteIncrementHistoryMutation,
  useGetSalaryPaymentsQuery,
  useGetSalaryPaymentByIdQuery,
  useCreateSalaryPaymentMutation,
  useUpdateSalaryPaymentMutation,
  useDeleteSalaryPaymentMutation,
  useGetSalaryStructuresQuery,
  useGetSalaryStructureByIdQuery,
  useCreateSalaryStructureMutation,
  useUpdateSalaryStructureMutation,
  useDeleteSalaryStructureMutation,
} = payrollApi;
