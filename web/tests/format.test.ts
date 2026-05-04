import { describe, expect, it } from "vitest";

import { formatClusterDate } from "../lib/format";

describe("formatClusterDate", () => {
  it("returns a fallback label for missing values", () => {
    expect(formatClusterDate("")).toBe("Unknown date");
  });
});
