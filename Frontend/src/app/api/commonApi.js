import { baseApi } from "../baseApi";

export const commonApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    uploadFile: builder.mutation({
      query: (formData) => ({
        url: "/api/v1/common/upload/document/",
        method: "POST",
        body: formData,
      }),
      invalidatesTags: ["Files"],
    }),
  }),
});

export const {
  useUploadFileMutation,
} = commonApi;
