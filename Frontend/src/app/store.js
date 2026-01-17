import { configureStore } from "@reduxjs/toolkit";
import settingsReducer from "./settingsSlice";
import { allSlices } from "./allSlices";

const store = configureStore({
  reducer: {
    settings: settingsReducer,
    [allSlices.reducerPath]: allSlices.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(allSlices.middleware),
});

export default store;
