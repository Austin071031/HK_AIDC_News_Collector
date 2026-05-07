import type { ClusterListResponse, ClusterDetailResponse, ActionPayload, Source, Keyword } from "./types";

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

export async function getSources(): Promise<Source[]> {
  const response = await fetch(`${API_BASE_URL}/api/sources`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch sources");
  return response.json();
}

export async function createSource(payload: Omit<Source, "id">): Promise<Source> {
  const response = await fetch(`${API_BASE_URL}/api/sources`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Failed to create source");
  return response.json();
}

export async function deleteSource(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/sources/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete source");
}

export async function getKeywords(): Promise<Keyword[]> {
  const response = await fetch(`${API_BASE_URL}/api/keywords`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch keywords");
  return response.json();
}

export async function createKeyword(payload: Omit<Keyword, "id">): Promise<Keyword> {
  const response = await fetch(`${API_BASE_URL}/api/keywords`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Failed to create keyword");
  return response.json();
}

export async function deleteKeyword(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/keywords/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete keyword");
}
