import { baseApi } from "../baseApi";

export const employeeApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
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
  }),
});

export const {
  useGetDepartmentsQuery,
  useGetDepartmentByIdQuery,
  useCreateDepartmentMutation,
  useUpdateDepartmentMutation,
  useDeleteDepartmentMutation,
  useGetDesignationsQuery,
  useGetDesignationByIdQuery,
  useCreateDesignationMutation,
  useUpdateDesignationMutation,
  useDeleteDesignationMutation,
  useGetEmployeeDetailsQuery,
  useGetEmployeeDetailByIdQuery,
  useCreateEmployeeDetailMutation,
  useUpdateEmployeeDetailMutation,
  useDeleteEmployeeDetailMutation,
  useGetEmployeeAttendancesQuery,
  useGetEmployeeAttendanceByIdQuery,
  useCreateEmployeeAttendanceMutation,
  useUpdateEmployeeAttendanceMutation,
  useDeleteEmployeeAttendanceMutation,
  useGetEmployeeDocumentsQuery,
  useGetEmployeeDocumentByIdQuery,
  useCreateEmployeeDocumentMutation,
  useUpdateEmployeeDocumentMutation,
  useDeleteEmployeeDocumentMutation,
  useGetEmployeePerformancesQuery,
  useGetEmployeePerformanceByIdQuery,
  useCreateEmployeePerformanceMutation,
  useUpdateEmployeePerformanceMutation,
  useDeleteEmployeePerformanceMutation,
} = employeeApi;
