import { describe, expect, it } from "vitest";
import {
  EMPTY,
  formatDate,
  formatDateTime,
  formatEnum,
  formatMoney,
  formatName,
  formatNumber,
  formatPercent,
  formatQuantity,
  formatTime,
  todayISO,
} from "./format";

describe("formatMoney", () => {
  it("uses Indian grouping and always shows paise", () => {
    expect(formatMoney(124000)).toBe("₹1,24,000.00");
    expect(formatMoney("1240.5")).toBe("₹1,240.50");
    expect(formatMoney(0)).toBe("₹0.00");
  });

  it("does not render rubbish as a number", () => {
    for (const bad of [null, undefined, "", "abc", NaN]) {
      expect(formatMoney(bad)).toBe(EMPTY);
    }
  });

  it("keeps the sign on a refund", () => {
    expect(formatMoney(-450)).toContain("450.00");
    expect(formatMoney(-450)).toMatch(/^-/);
  });
});

describe("numbers", () => {
  it("groups counts without decimals", () => {
    expect(formatNumber(1234567)).toBe("12,34,567");
  });

  it("shows quantity decimals only when there are any", () => {
    expect(formatQuantity(12)).toBe("12");
    expect(formatQuantity(12.5)).toBe("12.500");
    expect(formatQuantity(null)).toBe(EMPTY);
  });

  it("formats percentages", () => {
    expect(formatPercent(12.34)).toBe("12.3%");
  });
});

describe("dates", () => {
  it("renders an unambiguous date", () => {
    expect(formatDate("2026-09-18")).toBe("18 Sep 2026");
  });

  it("keeps a bare date on its own calendar day", () => {
    expect(formatDate("2026-01-01")).toBe("01 Jan 2026");
  });

  it("renders a UTC timestamp in the display zone", () => {
    expect(formatDateTime("2026-09-18T09:05:00Z")).toContain("18 Sep 2026");
    expect(formatTime("2026-09-18T09:05:00Z")).toMatch(/02:35\s?pm/i);
  });

  it("does not print Invalid Date", () => {
    for (const bad of [null, undefined, "", "not-a-date"]) {
      expect(formatDate(bad)).toBe(EMPTY);
      expect(formatDateTime(bad)).toBe(EMPTY);
      expect(formatTime(bad)).toBe(EMPTY);
    }
  });

  it("gives today in a shape <input type=date> accepts", () => {
    expect(todayISO()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});

describe("labels", () => {
  it("reads both the API value and the SQL member name", () => {
    expect(formatEnum("full-time")).toBe("Full time");
    expect(formatEnum("PARTIALLY_PAID")).toBe("Partially paid");
    expect(formatEnum(null)).toBe(EMPTY);
  });

  it("finds a name in whichever shape the API returned", () => {
    expect(formatName({ first_name: "Asha", last_name: "Rao" })).toBe("Asha Rao");
    expect(formatName({ full_name: "Asha Rao" })).toBe("Asha Rao");
    expect(formatName({ email: "asha@cafe.com" })).toBe("asha@cafe.com");
    expect(formatName(null)).toBe(EMPTY);
  });
});
