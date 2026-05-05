export type ClusterListItem = {
  cluster_id: string;
  headline: string;
  summary?: string;
  publish_date?: string;
  region?: string;
  topic_tags?: string[];
  extracted_entities?: string[];
  source_count?: number;
};

export type ClusterListResponse = {
  items: ClusterListItem[];
};

export type Article = {
  id: number;
  title: string;
  url: string;
  source_name: string;
  crawled_at: string;
};

export type ClusterDetailResponse = {
  id: number;
  cluster_id: string;
  headline: string;
  rationale: string;
  extracted_entities: string[];
  articles: Article[];
};

export type ActionPayload = {
  is_hidden: boolean;
  is_favorite: boolean;
  notes: string | null;
  tags: string[] | null;
};
