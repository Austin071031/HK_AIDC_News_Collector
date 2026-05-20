import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SplitViewDashboard from "../app/SplitViewDashboard";
import * as api from "../lib/api";
import type { SourceWithCount, SourceArticle } from "../lib/types";

// AnalystActionPanel has been removed

vi.mock("../lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../lib/api")>();
  return {
    ...actual,
    getSourceArticles: vi.fn(),
  };
});

describe("SplitViewDashboard", () => {
  const initialSources: SourceWithCount[] = [
    {
      id: 1,
      name: "Source 1",
      base_url: "http://source1.com",
      region: "Hong Kong",
      language: "en",
      source_type: "news",
      discovery_mode: "rss",
      priority: 1,
      active: true,
      article_count: 5
    },
    {
      id: 2,
      name: "Source 2",
      base_url: "http://source2.com",
      region: "Mainland China",
      language: "zh",
      source_type: "news",
      discovery_mode: "rss",
      priority: 2,
      active: true,
      article_count: 3
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it("renders the list of sources initially", () => {
    render(<SplitViewDashboard initialSources={initialSources} />);
    expect(screen.getByText("Source 1")).toBeDefined();
    expect(screen.getByText("Source 2")).toBeDefined();
    expect(screen.getByText("Select a source to view articles")).toBeDefined();
  });

  it("shows 'No sources found' when the initial list is empty", () => {
    render(<SplitViewDashboard initialSources={[]} />);
    expect(screen.getByText("No sources found.")).toBeDefined();
  });

  it("fetches and displays source articles when a source is clicked", async () => {
    const user = userEvent.setup();
    const mockArticles: SourceArticle[] = [
      {
        id: 101,
        title: "Test Article 101",
        url: "http://test.com/101",
        published_at: "2026-05-07T12:00:00Z",
        enrichment: {
          summary: "AI Summary for Article 101",
          relevance: "direct",
          tags: ["test"]
        }
      }
    ];

    vi.mocked(api.getSourceArticles).mockResolvedValue(mockArticles);

    render(<SplitViewDashboard initialSources={initialSources} />);
    
    const item = screen.getByText("Source 1");
    await user.click(item);

    await waitFor(() => {
      expect(screen.getByText("Test Article 101")).toBeDefined();
    });

    expect(screen.getByText("AI Summary for Article 101")).toBeDefined();
  });
});