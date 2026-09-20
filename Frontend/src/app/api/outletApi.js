import { baseApi } from "../baseApi";

export const outletApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getOutlets: builder.query({
      query: (params = {}) => ({
        url: "/api/v1/outlets/",
        method: "GET",
        params,
      }),
      providesTags: ["Outlets"],
    }),
    getOutletById: builder.query({
      query: (id) => ({ url: `/api/v1/outlets/${id}`, method: "GET" }),
      providesTags: (result, error, id) => [{ type: "Outlets", id }],
    }),
    createOutlet: builder.mutation({
      query: (body) => ({ url: "/api/v1/outlets/", method: "POST", body }),
      invalidatesTags: ["Outlets"],
    }),
    updateOutlet: builder.mutation({
      query: ({ id, ...body }) => ({
        url: `/api/v1/outlets/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: "Outlets", id },
        "Outlets",
      ],
    }),
  }),
});

export const {
  useGetOutletsQuery,
  useGetOutletByIdQuery,
  useCreateOutletMutation,
  useUpdateOutletMutation,
} = outletApi;
