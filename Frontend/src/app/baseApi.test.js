import { describe, expect, it } from "vitest";
import { baseApi, TAG_TYPES } from "./baseApi";
import * as hooks from "./allSlices";

const apiModules = import.meta.glob("./api/*.js", { eager: true, query: "?raw", import: "default" });

describe("the API surface", () => {
  it("has at least one domain module, and all of them attached", () => {
    expect(Object.keys(apiModules).length).toBeGreaterThan(0);
    expect(Object.keys(baseApi.endpoints).length).toBeGreaterThan(100);
  });

  it("declares every tag its endpoints reference", () => {
    const referenced = new Set();

    for (const source of Object.values(apiModules)) {
      for (const m of source.matchAll(/type:\s*"([A-Za-z]+)"/g)) referenced.add(m[1]);
      for (const m of source.matchAll(/(?:provides|invalidates)Tags:\s*\[([^\]]*)\]/g)) {
        for (const t of m[1].matchAll(/"([A-Za-z]+)"/g)) referenced.add(t[1]);
      }
    }

    const undeclared = [...referenced].filter((tag) => !TAG_TYPES.includes(tag));
    expect(undeclared).toEqual([]);
  });

  it("exports a hook for every endpoint", () => {
    const missing = Object.entries(baseApi.endpoints)
      .map(([name, endpoint]) => {
        const suffix = endpoint.useQuery ? "Query" : "Mutation";
        return `use${name[0].toUpperCase()}${name.slice(1)}${suffix}`;
      })
      .filter((hook) => typeof hooks[hook] !== "function");

    expect(missing).toEqual([]);
  });

  it("keeps the reducer path the store is mounted under", () => {
    expect(baseApi.reducerPath).toBe("allSlices");
  });
});
