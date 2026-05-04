import type { ClusterListResponse } from "./types";

const API_BASE_URL = "http://localhost:8000";

export async function getClusters(): Promise<ClusterListResponse> {
  const response = await fetch(`${API_BASE_URL}/api/clusters`, {
    cache: "no-store",
  });

  return response.json();
}
