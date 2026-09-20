/**
 * @vitest-environment jsdom
 */
import { describe, expect, it } from "vitest";
import { themes, themeLabels, deriveTokens, applyTheme } from "./themes";
import { contrastRatio, parseTriple, mix, onColor, modeOf } from "./color";

const AA_TEXT = 4.5;
const AA_LARGE = 3.0;

const FILLED = ["primary", "secondary", "accent", "success", "warning", "error", "info"];
const PALETTE_KEYS = Object.keys(themes.mysticForest);

describe("colour maths", () => {
  it("rejects a malformed triple instead of silently producing black", () => {
    expect(() => parseTriple("34,197")).toThrow();
    expect(() => parseTriple("34 197 300")).toThrow();
  });

  it("matches known WCAG ratios", () => {
    expect(contrastRatio("255 255 255", "0 0 0")).toBeCloseTo(21, 5);
    expect(contrastRatio("34 197 94", "34 197 94")).toBeCloseTo(1, 5);
  });

  it("mixes towards the second colour", () => {
    expect(mix("0 0 0", "255 255 255", 0)).toBe("0 0 0");
    expect(mix("0 0 0", "255 255 255", 1)).toBe("255 255 255");
    expect(mix("0 0 0", "100 100 100", 0.5)).toBe("50 50 50");
  });

  it("classifies light and dark grounds", () => {
    expect(modeOf("255 255 255")).toBe("light");
    expect(modeOf("19 35 23")).toBe("dark");
  });

  it("picks the higher-contrast foreground", () => {
    expect(onColor("253 224 71")).not.toBe("255 255 255");
    expect(onColor("17 24 39")).toBe("255 255 255");
  });
});

describe.each(Object.keys(themes))("theme %s", (name) => {
  const palette = themes[name];
  const tokens = deriveTokens(palette);

  it("declares every palette token", () => {
    expect(Object.keys(palette).sort()).toEqual(PALETTE_KEYS.sort());
  });

  it("has a plain-language label", () => {
    expect(themeLabels[name]).toBeTruthy();
  });

  it.each(FILLED)("on-%s passes WCAG AA against its background", (token) => {
    const ratio = contrastRatio(palette[`--color-${token}`], tokens[`--color-on-${token}`]);
    expect(ratio).toBeGreaterThanOrEqual(AA_TEXT);
  });

  it("body text passes AA on the background", () => {
    expect(
      contrastRatio(palette["--color-background"], tokens["--color-foreground"]),
    ).toBeGreaterThanOrEqual(AA_TEXT);
  });

  it("muted text is quieter than body text but still legible", () => {
    const body = contrastRatio(palette["--color-background"], tokens["--color-foreground"]);
    const muted = contrastRatio(palette["--color-background"], tokens["--color-muted-foreground"]);
    expect(muted).toBeGreaterThanOrEqual(AA_LARGE);
    expect(muted).toBeLessThan(body);
  });

  it("the muted surface is distinguishable from the surface it sits on", () => {
    expect(
      contrastRatio(palette["--color-surface"], tokens["--color-muted"]),
    ).toBeGreaterThan(1.02);
  });

  it("derives every token the shared components reference", () => {
    for (const key of [
      "--color-foreground",
      "--color-muted",
      "--color-muted-foreground",
      "--color-scrim",
      "--color-sheen",
      "--color-star",
      "--color-star-empty",
      "--theme-mode",
    ]) {
      expect(tokens[key]).toBeTruthy();
    }
  });
});

describe("applyTheme", () => {
  it("accepts a theme key and sets colour-scheme for native controls", () => {
    applyTheme("mysticForest");
    expect(document.documentElement.style.getPropertyValue("--color-on-primary")).toBeTruthy();
    expect(document.documentElement.style.colorScheme).toBe("dark");
    applyTheme("frostVale");
    expect(document.documentElement.style.colorScheme).toBe("light");
  });

  it("ignores rubbish rather than blanking the UI", () => {
    const before = document.documentElement.style.getPropertyValue("--color-primary");
    applyTheme("no-such-theme");
    expect(document.documentElement.style.getPropertyValue("--color-primary")).toBe(before);
  });
});
