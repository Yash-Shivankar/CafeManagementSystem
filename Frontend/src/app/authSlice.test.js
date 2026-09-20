import { describe, expect, it } from "vitest";
import reducer, {
  bootstrapSettled,
  selectBootstrapped,
  selectIsSignedIn,
  selectPermissions,
  selectRole,
  selectUser,
  sessionEnded,
  sessionStarted,
} from "./authSlice";

const user = {
  id: 3,
  email: "asha@cafe.com",
  role: "Manager",
  permissions: { inventory: ["view", "create"], users: ["view"] },
};

describe("authSlice", () => {
  it("starts signed out and undecided", () => {
    const state = reducer(undefined, { type: "@@INIT" });
    expect(selectIsSignedIn({ auth: state })).toBe(false);
    expect(selectBootstrapped({ auth: state })).toBe(false);
  });

  it("records a session and what that user may do", () => {
    const state = reducer(undefined, sessionStarted(user));
    expect(selectUser({ auth: state })).toEqual(user);
    expect(selectIsSignedIn({ auth: state })).toBe(true);
    expect(selectRole({ auth: state })).toBe("Manager");
    expect(selectPermissions({ auth: state })).toEqual(user.permissions);
    expect(selectBootstrapped({ auth: state })).toBe(true);
  });

  it("clears everything on sign-out", () => {
    const signedIn = reducer(undefined, sessionStarted(user));
    const state = reducer(signedIn, sessionEnded());
    expect(selectUser({ auth: state })).toBeNull();
    expect(selectIsSignedIn({ auth: state })).toBe(false);
    expect(selectPermissions({ auth: state })).toEqual({});
  });

  it("distinguishes 'undecided' from 'signed out'", () => {
    const undecided = reducer(undefined, { type: "@@INIT" });
    const decided = reducer(undecided, bootstrapSettled());

    expect(selectIsSignedIn({ auth: undecided })).toBe(false);
    expect(selectIsSignedIn({ auth: decided })).toBe(false);
    expect(selectBootstrapped({ auth: undecided })).toBe(false);
    expect(selectBootstrapped({ auth: decided })).toBe(true);
  });

  it("bumps the epoch on every session change, so a stale tab can tell", () => {
    let state = reducer(undefined, { type: "@@INIT" });
    const start = state.epoch;
    state = reducer(state, sessionStarted(user));
    state = reducer(state, sessionEnded());
    expect(state.epoch).toBe(start + 2);
  });

  it("treats a session with no user payload as signed out", () => {
    const state = reducer(undefined, sessionStarted(undefined));
    expect(selectIsSignedIn({ auth: state })).toBe(false);
    expect(selectBootstrapped({ auth: state })).toBe(true);
  });
});
