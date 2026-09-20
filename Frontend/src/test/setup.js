import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";
import "@testing-library/jest-dom/vitest";

// globals flag: a leaked render makes the *next* test fail, which is the most

afterEach(() => {
  cleanup();
});
