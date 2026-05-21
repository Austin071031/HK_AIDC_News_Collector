import type { ClusterListResponse, ClusterDetailResponse, ActionPayload, Source, Keyword, SourceWithCount, SourceArticle } from "./types";

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

export async function getSources(
  searchParams?: { [key: string]: string | string[] | undefined }
): Promise<SourceWithCount[]> {
  const url = new URL(`${API_BASE_URL}/api/sources`);
  url.searchParams.append("with_counts", "true");
  
  if (searchParams) {
    Object.entries(searchParams).forEach(([key, value]) => {
      if (value) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  
  const response = await fetch(url.toString(), { cache: "no-store" });
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

export async function updateSource(id: number, payload: Partial<Source>): Promise<Source> {
  const response = await fetch(`${API_BASE_URL}/api/sources/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Failed to update source");
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

export async function getSourceArticles(
  sourceId: string,
  searchParams?: { [key: string]: string | string[] | undefined }
): Promise<SourceArticle[]> {
  const url = new URL(`${API_BASE_URL}/api/sources/${sourceId}/articles`);
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
  if (!response.ok) throw new Error("Failed to fetch source articles");
  return response.json();
}

export async function getArticles(
  searchParams?: { [key: string]: string | string[] | undefined }
): Promise<SourceArticle[]> {
  const url = new URL(`${API_BASE_URL}/api/articles`);
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
  if (!response.ok) throw new Error("Failed to fetch articles");
  return response.json();
}

export async function getArticleContent(articleId: number): Promise<{ raw_text: string; raw_html: string }> {
  const response = await fetch(`${API_BASE_URL}/api/articles/${articleId}/content`, {
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Failed to fetch article content");
  return response.json();
}

export async function cleanupDatabase(): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/jobs/cleanup`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("Failed to clean up database");
  return response.json();
}

export async function getConfig(key: string): Promise<{ key: string; value: string | null }> {
  const response = await fetch(`${API_BASE_URL}/api/config/${key}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch config");
  return response.json();
}

export async function updateConfig(key: string, value: string): Promise<{ key: string; value: string | null }> {
  const response = await fetch(`${API_BASE_URL}/api/config/${key}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value }),
  });
  if (!response.ok) throw new Error("Failed to update config");
  return response.json();
}

