import type { ClusterListResponse, ClusterDetailResponse, ActionPayload } from "./types";

const API_BASE_URL = "http://localhost:8000";

export async function getClusters(
  searchParams?: { [key: string]: string | string[] | undefined }
): Promise<ClusterListResponse> {
  const url = new URL(`${API_BASE_URL}/api/clusters`);
  if (searchParams) {
    Object.entries(searchParams).forEach(([key, value]) => {
      if (value) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  
  const response = await fetch(url.toString(), {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch clusters");
  }

  return response.json();
}

export async function getClusterDetail(clusterId: string): Promise<ClusterDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/api/clusters/${clusterId}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch cluster details");
  }

  return response.json();
}

export async function submitClusterAction(clusterId: string, payload: ActionPayload) {
  const response = await fetch(`${API_BASE_URL}/api/clusters/${clusterId}/actions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to submit action");
  }

  return response.json();
}
