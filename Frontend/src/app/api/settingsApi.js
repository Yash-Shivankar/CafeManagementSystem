import { baseApi } from "../baseApi";

export const settingsApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
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
  }),
});

export const {
  useGetSettingsQuery,
  useGetSettingByIdQuery,
  useCreateSettingMutation,
  useUpdateSettingMutation,
  useDeleteSettingMutation,
} = settingsApi;
