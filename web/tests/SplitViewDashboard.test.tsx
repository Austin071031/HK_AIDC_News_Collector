import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SplitViewDashboard from "../app/SplitViewDashboard";
import * as api from "../lib/api";

// Mock AnalystActionPanel so we don't need to render its complexity
vi.mock("../app/clusters/[clusterId]/AnalystActionPanel", () => {
  return {
    default: ({ clusterId }: { clusterId: string }) => (
      <div data-testid="analyst-action-panel">Analyst Panel for {clusterId}</div>
    )
  };
});

vi.mock("../lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../lib/api")>();
  return {
    ...actual,
    getClusterDetail: vi.fn(),
  };
});

describe("SplitViewDashboard", () => {
  const initialClusters = [
    {
      cluster_id: "c-1",
      headline: "Test Headline 1",
      publish_date: "2026-05-07T12:00:00Z",
      region: "Hong Kong",
    },
    {
      cluster_id: "c-2",
      headline: "Test Headline 2",
      publish_date: "2026-05-06T12:00:00Z",
      region: "Mainland China",
    }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it("renders the list of clusters initially", () => {
    render(<SplitViewDashboard initialClusters={initialClusters} />);
    expect(screen.getByText("Test Headline 1")).toBeDefined();
    expect(screen.getByText("Test Headline 2")).toBeDefined();
    expect(screen.getByText("Select a cluster to view details")).toBeDefined();
  });

  it("shows 'No clusters found' when the initial list is empty", () => {
    render(<SplitViewDashboard initialClusters={[]} />);
    expect(screen.getByText("No clusters found.")).toBeDefined();
  });

  it("fetches and displays cluster details when a cluster is clicked", async () => {
    const user = userEvent.setup();
    const mockDetail = {
      id: "c-1",
      cluster_id: "c-1",
      headline: "Test Headline 1 Details",
      rationale: "AI Summary for Test 1",
      articles: [
        { id: "a-1", title: "Article 1", url: "http://test.com/1", source_name: "Source 1" }
      ]
    };

    vi.mocked(api.getClusterDetail).mockResolvedValue(mockDetail as any);

    render(<SplitViewDashboard initialClusters={initialClusters} />);
    
    const item = screen.getByText("Test Headline 1");
    await user.click(item);

    await waitFor(() => {
      expect(screen.getByText("Test Headline 1 Details")).toBeDefined();
    });

    expect(screen.getByText("AI Summary for Test 1")).toBeDefined();
    expect(screen.getByText("Article 1")).toBeDefined();
    expect(screen.getByText("Source 1")).toBeDefined();
    expect(screen.getByTestId("analyst-action-panel").textContent).toContain("Analyst Panel for c-1");
  });
});
