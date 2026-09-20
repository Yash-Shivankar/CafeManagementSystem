import { configureStore } from "@reduxjs/toolkit";
import settingsReducer from "./settingsSlice";
import authReducer from "./authSlice";
import { allSlices } from "./allSlices";
import { authService } from "../services/auth";

const store = configureStore({
  reducer: {
    auth: authReducer,
    settings: settingsReducer,
    [allSlices.reducerPath]: allSlices.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(allSlices.middleware),
});

authService.bindStore(store);

export default store;
