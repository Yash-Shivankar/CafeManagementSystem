import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { authService } from "../services/auth";
import { BaseUrl } from "../config/config";

export const allSlices = createApi({
  reducerPath: "allSlices",
  baseQuery: fetchBaseQuery({
    baseUrl: BaseUrl,
    prepareHeaders: (headers) => {
      const token = authService.getToken();

      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),

  endpoints: (builder) => ({
    // Login
    login: builder.mutation({
      query: (payload) => ({
        url: "/api/v1/auth/login/",
        method: "POST",
        body: payload,
      }),
    }),

    // ApplicationSettings
    getSettings: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/settings/",
        method: "GET",
        params,
      }),
      providesTags: ["Settings"],
    }),
    getSettingById: builder.query({
      query: (id) => ({
        url: `/api/v1/settings/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Settings", id }],
    }),
    createSetting: builder.mutation({
      query: (body) => ({
        url: "/api/v1/settings/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Settings"],
    }),
    updateSetting: builder.mutation({
      query: ({ key, value }) => ({
        url: `/api/v1/settings/${key}`,
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
        url: `/api/v1/settings/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Settings"],
    }),

    // Bookings
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

    // Upload Document
    uploadFile: builder.mutation({
      query: (formData) => ({
        url: "/api/v1/common/upload/document/",
        method: "POST",
        body: formData,
      }),
      invalidatesTags: ["Files"],
    }),

    // CustomerFeedbacks
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

    // CustomerInvoices
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

    // Dashboard
    getDashboardStats: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/dashboard/stats",
        method: "GET",
        params,
      }),
      providesTags: ["Dashboard"],
    }),

    // Departments
    getDepartments: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/departments/",
        method: "GET",
        params,
      }),
      providesTags: ["Departments"],
    }),
    getDepartmentById: builder.query({
      query: (id) => ({
        url: `/api/v1/departments/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Departments", id }],
    }),
    createDepartment: builder.mutation({
      query: (body) => ({
        url: "/api/v1/departments/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Departments"],
    }),
    updateDepartment: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/departments/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Departments", id },
        "Departments",
      ],
    }),
    deleteDepartment: builder.mutation({
      query: (id) => ({
        url: `/api/v1/departments/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Departments"],
    }),

    // Designation
    getDesignations: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/designations/",
        method: "GET",
        params,
      }),
      providesTags: ["Designations"],
    }),
    getDesignationById: builder.query({
      query: (id) => ({
        url: `/api/v1/designations/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "Designations", id }],
    }),
    createDesignation: builder.mutation({
      query: (body) => ({
        url: "/api/v1/designations/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Designations"],
    }),
    updateDesignation: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/designations/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Designations", id },
        "Designations",
      ],
    }),
    deleteDesignation: builder.mutation({
      query: (id) => ({
        url: `/api/v1/designations/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Designations"],
    }),

    // EmployeeAttendances
    getEmployeeAttendances: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/employee-attendances/",
        method: "GET",
        params,
      }),
      providesTags: ["EmployeeAttendances"],
    }),
    getEmployeeAttendanceById: builder.query({
      query: (id) => ({
        url: `/api/v1/employee-attendances/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [
        { type: "EmployeeAttendances", id },
      ],
    }),
    createEmployeeAttendance: builder.mutation({
      query: (body) => ({
        url: "/api/v1/employee-attendances/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["EmployeeAttendances"],
    }),
    updateEmployeeAttendance: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/employee-attendances/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "EmployeeAttendances", id },
        "EmployeeAttendances",
      ],
    }),
    deleteEmployeeAttendance: builder.mutation({
      query: (id) => ({
        url: `/api/v1/employee-attendances/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["EmployeeAttendances"],
    }),

    // EmployeeDetails
    getEmployeeDetails: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/employee-details/",
        method: "GET",
        params,
      }),
      providesTags: ["EmployeeDetails"],
    }),
    getEmployeeDetailById: builder.query({
      query: (id) => ({
        url: `/api/v1/employee-details/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "EmployeeDetails", id }],
    }),
    createEmployeeDetail: builder.mutation({
      query: (body) => ({
        url: "/api/v1/employee-details/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["EmployeeDetails"],
    }),
    updateEmployeeDetail: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/employee-details/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "EmployeeDetails", id },
        "EmployeeDetails",
      ],
    }),
    deleteEmployeeDetail: builder.mutation({
      query: (id) => ({
        url: `/api/v1/employee-details/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["EmployeeDetails"],
    }),

    // EmployeeDocuments
    getEmployeeDocuments: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/employee-documents/",
        method: "GET",
        params,
      }),
      providesTags: ["EmployeeDocuments"],
    }),
    getEmployeeDocumentById: builder.query({
      query: (id) => ({
        url: `/api/v1/employee-documents/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [{ type: "EmployeeDocuments", id }],
    }),
    createEmployeeDocument: builder.mutation({
      query: (body) => ({
        url: "/api/v1/employee-documents/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["EmployeeDocuments"],
    }),
    updateEmployeeDocument: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/employee-documents/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "EmployeeDocuments", id },
        "EmployeeDocuments",
      ],
    }),
    deleteEmployeeDocument: builder.mutation({
      query: (id) => ({
        url: `/api/v1/employee-documents/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["EmployeeDocuments"],
    }),

    // EmployeePerformances
    getEmployeePerformances: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/employee-performances/",
        method: "GET",
        params,
      }),
      providesTags: ["EmployeePerformances"],
    }),
    getEmployeePerformanceById: builder.query({
      query: (id) => ({
        url: `/api/v1/employee-performances/${id}`,
        method: "GET",
      }),
      providesTags: (result, error, id) => [
        { type: "EmployeePerformances", id },
      ],
    }),
    createEmployeePerformance: builder.mutation({
      query: (body) => ({
        url: "/api/v1/employee-performances/",
        method: "POST",
        body,
      }),
      invalidatesTags: ["EmployeePerformances"],
    }),
    updateEmployeePerformance: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/employee-performances/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "EmployeePerformances", id },
        "EmployeePerformances",
      ],
    }),
    deleteEmployeePerformance: builder.mutation({
      query: (id) => ({
        url: `/api/v1/employee-performances/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["EmployeePerformances"],
    }),

    // Incentives
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

    // IncrementHistories
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

    // InventoryCategories
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

    // InventoryItems
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

    // InventoryLogs
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

    // Payments
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

    // ProfitLoss
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

    // Roles
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

    // SalaryPayments
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

    // SalaryStructures
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

    // Services
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

    // Tables
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

    // Users
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

  // Bookings
  useGetBookingsQuery,
  useGetBookingByIdQuery,
  useCreateBookingMutation,
  useUpdateBookingMutation,
  useDeleteBookingMutation,

  //  Upload Document
  useUploadFileMutation,

  // CustomerFeedbacks
  useGetCustomerFeedbacksQuery,
  useGetCustomerFeedbackByIdQuery,
  useCreateCustomerFeedbackMutation,
  useUpdateCustomerFeedbackMutation,
  useDeleteCustomerFeedbackMutation,

  // CustomerInvoices
  useGetCustomerInvoicesQuery,
  useGetCustomerInvoiceByIdQuery,
  useCreateCustomerInvoiceMutation,
  useUpdateCustomerInvoiceMutation,
  useDeleteCustomerInvoiceMutation,

  // Dashboard
  useGetDashboardStatsQuery,

  // Departments
  useGetDepartmentsQuery,
  useGetDepartmentByIdQuery,
  useCreateDepartmentMutation,
  useUpdateDepartmentMutation,
  useDeleteDepartmentMutation,

  // Designations
  useGetDesignationsQuery,
  useGetDesignationByIdQuery,
  useCreateDesignationMutation,
  useUpdateDesignationMutation,
  useDeleteDesignationMutation,

  // EmployeeAttendances
  useGetEmployeeAttendancesQuery,
  useGetEmployeeAttendanceByIdQuery,
  useCreateEmployeeAttendanceMutation,
  useUpdateEmployeeAttendanceMutation,
  useDeleteEmployeeAttendanceMutation,

  // EmployeeDetails
  useGetEmployeeDetailsQuery,
  useGetEmployeeDetailByIdQuery,
  useCreateEmployeeDetailMutation,
  useUpdateEmployeeDetailMutation,
  useDeleteEmployeeDetailMutation,

  // EmployeeDocuments
  useGetEmployeeDocumentsQuery,
  useGetEmployeeDocumentByIdQuery,
  useCreateEmployeeDocumentMutation,
  useUpdateEmployeeDocumentMutation,
  useDeleteEmployeeDocumentMutation,

  // EmployeePerformances
  useGetEmployeePerformancesQuery,
  useGetEmployeePerformanceByIdQuery,
  useCreateEmployeePerformanceMutation,
  useUpdateEmployeePerformanceMutation,
  useDeleteEmployeePerformanceMutation,

  // Incentives
  useGetIncentivesQuery,
  useGetIncentiveByIdQuery,
  useCreateIncentiveMutation,
  useUpdateIncentiveMutation,
  useDeleteIncentiveMutation,

  // IncrementHistories
  useGetIncrementHistoriesQuery,
  useGetIncrementHistoryByIdQuery,
  useCreateIncrementHistoryMutation,
  useUpdateIncrementHistoryMutation,
  useDeleteIncrementHistoryMutation,

  // InventoryCategories
  useGetInventoryCategoriesQuery,
  useGetInventoryCategoryByIdQuery,
  useCreateInventoryCategoryMutation,
  useUpdateInventoryCategoryMutation,
  useDeleteInventoryCategoryMutation,

  // InventoryItems
  useGetInventoryItemsQuery,
  useGetInventoryItemByIdQuery,
  useCreateInventoryItemMutation,
  useUpdateInventoryItemMutation,
  useDeleteInventoryItemMutation,

  // InventoryLogs
  useGetInventoryLogsQuery,
  useCreateInventoryLogMutation,

  // Payments
  useGetPaymentsQuery,
  useGetPaymentByIdQuery,
  useCreatePaymentMutation,
  useUpdatePaymentMutation,
  useDeletePaymentMutation,

  // ProfitLoss
  useGetEarningsQuery,
  useGetEarningByIdQuery,
  useCreateEarningMutation,
  useUpdateEarningMutation,
  useDeleteEarningMutation,

  // Roles
  useGetRolesQuery,
  useGetRoleByIdQuery,
  useCreateRoleMutation,
  useUpdateRoleMutation,
  useDeleteRoleMutation,

  // SalaryPayments
  useGetSalaryPaymentsQuery,
  useGetSalaryPaymentByIdQuery,
  useCreateSalaryPaymentMutation,
  useUpdateSalaryPaymentMutation,
  useDeleteSalaryPaymentMutation,

  // SalaryStructures
  useGetSalaryStructuresQuery,
  useGetSalaryStructureByIdQuery,
  useCreateSalaryStructureMutation,
  useUpdateSalaryStructureMutation,
  useDeleteSalaryStructureMutation,

  // Services
  useGetServicesQuery,
  useGetServiceByIdQuery,
  useCreateServiceMutation,
  useUpdateServiceMutation,
  useDeleteServiceMutation,

  // Tables
  useGetTablesQuery,
  useGetTableByIdQuery,
  useCreateTableMutation,
  useUpdateTableMutation,
  useDeleteTableMutation,

  // Users
  useGetUsersQuery,
  useGetUserByIdQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
} = allSlices;
