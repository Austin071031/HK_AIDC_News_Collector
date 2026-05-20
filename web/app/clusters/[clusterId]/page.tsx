import { getClusterDetail } from "../../../lib/api";
import { formatClusterDate } from "../../../lib/format";

type ClusterDetailPageProps = {
  params: Promise<{
    clusterId: string;
  }>;
};

export default async function ClusterDetailPage({
  params,
}: ClusterDetailPageProps) {
  const { clusterId } = await params;
  const cluster = await getClusterDetail(clusterId);

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "48px 24px",
        background: "#f3f7fb",
        color: "#08131a",
      }}
    >
      <div
        style={{
          maxWidth: "840px",
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
          gap: "24px",
        }}
      >
        <div style={{ marginBottom: "8px" }}>
          <a href="/" style={{ color: "#547086", textDecoration: "none", fontSize: "14px" }}>← Back to Dashboard</a>
        </div>
        
        <section
          style={{
            padding: "32px",
            borderRadius: "24px",
            background: "#ffffff",
            boxShadow: "0 24px 60px rgba(12, 36, 53, 0.12)",
          }}
        >
          <p
            style={{
              margin: 0,
              fontSize: "12px",
              letterSpacing: "0.2em",
              textTransform: "uppercase",
              color: "#547086",
            }}
          >
            Cluster Overview
          </p>
          <h1 style={{ margin: "12px 0 16px", fontSize: "36px", lineHeight: 1.2 }}>{cluster.headline}</h1>
          
          <div style={{ background: "#f8fbfd", padding: "20px", borderRadius: "12px", border: "1px solid #d8e4ee" }}>
            <h3 style={{ margin: "0 0 8px", fontSize: "14px", textTransform: "uppercase", color: "#547086" }}>Rationale</h3>
            <p style={{ margin: 0, color: "#0f3d5d", lineHeight: 1.6 }}>
              {cluster.rationale || "No rationale provided."}
            </p>
          </div>

          {cluster.extracted_entities && cluster.extracted_entities.length > 0 && (
            <div style={{ marginTop: "24px" }}>
              <h3 style={{ margin: "0 0 12px", fontSize: "14px", textTransform: "uppercase", color: "#547086" }}>Key Entities</h3>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {cluster.extracted_entities.map((entity) => (
                  <span key={entity} style={{ background: "#e5f0f9", color: "#0f3d5d", padding: "4px 12px", borderRadius: "16px", fontSize: "14px" }}>
                    {entity}
                  </span>
                ))}
              </div>
            </div>
          )}
        </section>

        <section
          style={{
            padding: "32px",
            borderRadius: "24px",
            background: "#ffffff",
            boxShadow: "0 24px 60px rgba(12, 36, 53, 0.12)",
          }}
        >
          <h2 style={{ margin: "0 0 20px", fontSize: "24px" }}>Related Articles ({cluster.articles.length})</h2>
          
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: "16px" }}>
            {cluster.articles.map(article => (
              <li key={article.id} style={{ padding: "16px", border: "1px solid #d8e4ee", borderRadius: "12px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                  <a href={article.url} target="_blank" rel="noreferrer" style={{ fontSize: "18px", color: "#0f3d5d", textDecoration: "none", fontWeight: 500 }}>
                    {article.title}
                  </a>
                </div>
                <div style={{ display: "flex", gap: "12px", fontSize: "13px", color: "#607586" }}>
                  <span>{article.source_name}</span>
                  <span>•</span>
                  <span>{formatClusterDate(article.crawled_at)}</span>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  );
}
