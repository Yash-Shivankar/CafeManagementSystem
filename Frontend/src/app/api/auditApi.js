import { baseApi } from "../baseApi";

export const auditApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getAuditLogs: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/audit-logs/",
        method: "GET",
        params,
      }),
      providesTags: ["AuditLogs"],
    }),
    getRecordHistory: builder.query({
      query: ({ tableName, recordId }) => ({
        url: `/api/v1/audit-logs/${tableName}/${recordId}`,
        method: "GET",
      }),
      providesTags: ["AuditLogs"],
    }),
  }),
});

export const {
  useGetAuditLogsQuery,
  useGetRecordHistoryQuery,
} = auditApi;
