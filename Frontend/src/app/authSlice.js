import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  user: null,
  bootstrapped: false,
  epoch: 0,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    sessionStarted: (state, action) => {
      state.user = action.payload ?? null;
      state.bootstrapped = true;
      state.epoch += 1;
    },
    sessionEnded: (state) => {
      state.user = null;
      state.bootstrapped = true;
      state.epoch += 1;
    },
    bootstrapSettled: (state) => {
      state.bootstrapped = true;
    },
  },
});

export const { sessionStarted, sessionEnded, bootstrapSettled } = authSlice.actions;

export const selectUser = (state) => state.auth.user;
export const selectIsSignedIn = (state) => Boolean(state.auth.user);
export const selectBootstrapped = (state) => state.auth.bootstrapped;
export const selectRole = (state) => state.auth.user?.role ?? null;
export const selectPermissions = (state) => state.auth.user?.permissions ?? {};

export default authSlice.reducer;
