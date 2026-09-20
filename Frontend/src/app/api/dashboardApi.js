import { baseApi } from "../baseApi";

export const dashboardApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getDashboardStats: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/dashboard/stats",
        method: "GET",
        params,
      }),
      providesTags: ["Dashboard"],
    }),
    closeDay: builder.mutation({
      query: (body) => ({
        url: "/api/v1/profit-loss/close-day",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Earning", "AuditLogs"],
    }),
    createMediaUrl: builder.mutation({
      query: (path) => ({
        url: "/api/v1/common/media-url",
        method: "POST",
        body: { path },
      }),
    }),
  }),
});

export const {
  useGetDashboardStatsQuery,
  useCloseDayMutation,
  useCreateMediaUrlMutation,
} = dashboardApi;
