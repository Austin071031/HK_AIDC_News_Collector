export type ClusterListItem = {
  cluster_id: string;
  headline: string;
  summary?: string;
  publish_date?: string;
};

export type ClusterListResponse = {
  items: ClusterListItem[];
};
