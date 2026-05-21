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

export interface Source {
  id: number;
  name: string;
  base_url: string;
  rss_url?: string | null;
  region: string;
  language: string;
  source_type: string;
  discovery_mode: string;
  priority: number;
  active: boolean;
}

export interface Keyword {
  id: number;
  keyword: string;
  active: boolean;
}

export interface ArticleEnrichment {
  summary: string;
  relevance: string;
  tags: string[];
  key_points?: string[];
  extracted_content?: string;
}

export interface SourceArticle {
  id: number;
  title: string;
  url: string;
  published_at: string | null;
  enrichment: ArticleEnrichment | null;
  source_name?: string;
  source_region?: string;
}

export interface SourceWithCount extends Source {
  article_count?: number;
}
