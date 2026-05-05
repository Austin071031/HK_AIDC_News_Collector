import { getClusters } from "../lib/api";
import { formatClusterDate } from "../lib/format";

type SearchParams = {
  region?: string;
  relevance?: string;
};

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const resolvedParams = await searchParams;
  const data = await getClusters(resolvedParams);

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "48px 24px",
        background:
          "linear-gradient(180deg, #06131d 0%, #0d2131 55%, #f3f7fb 55%, #f3f7fb 100%)",
        color: "#08131a",
      }}
    >
      <div
        style={{
          maxWidth: "960px",
          margin: "0 auto",
          display: "grid",
          gap: "24px",
        }}
      >
        <section
          style={{
            padding: "32px",
            borderRadius: "24px",
            background: "rgba(255, 255, 255, 0.08)",
            backdropFilter: "blur(14px)",
            color: "#f7fbff",
            boxShadow: "0 24px 80px rgba(0, 0, 0, 0.18)",
          }}
        >
          <p
            style={{
              margin: 0,
              fontSize: "12px",
              letterSpacing: "0.24em",
              textTransform: "uppercase",
              color: "#8fd3ff",
            }}
          >
            Daily Cluster Feed
          </p>
          <h1 style={{ margin: "12px 0 8px", fontSize: "40px" }}>
            AI Data Center News Monitor
          </h1>
          <p style={{ margin: 0, maxWidth: "60ch", color: "#d6e7f5" }}>
            Read the current cluster-first market feed for AI data center,
            telecom, power, and infrastructure developments.
          </p>
        </section>

        <section
          style={{
            padding: "24px",
            borderRadius: "24px",
            background: "#ffffff",
            boxShadow: "0 24px 60px rgba(12, 36, 53, 0.12)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "20px",
            }}
          >
            <h2 style={{ margin: 0, fontSize: "24px" }}>Latest Clusters</h2>
            <form method="get" style={{ display: "flex", gap: "12px" }}>
              <select 
                name="region" 
                defaultValue={resolvedParams.region || ""}
                style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #d8e4ee" }}
              >
                <option value="">All Regions</option>
                <option value="hong_kong">Hong Kong</option>
                <option value="mainland_china">Mainland China</option>
                <option value="southeast_asia">Southeast Asia</option>
              </select>
              <select 
                name="relevance" 
                defaultValue={resolvedParams.relevance || ""}
                style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #d8e4ee" }}
              >
                <option value="">All Relevance</option>
                <option value="direct">Direct</option>
                <option value="indirect">Indirect</option>
              </select>
              <button 
                type="submit"
                style={{ padding: "6px 16px", borderRadius: "6px", background: "#0f3d5d", color: "#fff", border: "none", cursor: "pointer" }}
              >
                Filter
              </button>
            </form>
          </div>

          <ul
            style={{
              listStyle: "none",
              margin: 0,
              padding: 0,
              display: "grid",
              gap: "16px",
            }}
          >
            {data.items.map((cluster) => (
              <li
                key={cluster.cluster_id}
                style={{
                  padding: "18px 20px",
                  borderRadius: "18px",
                  border: "1px solid #d8e4ee",
                  background: "#f8fbfd",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                  <a
                    href={`/clusters/${cluster.cluster_id}`}
                    style={{
                      color: "#0f3d5d",
                      fontSize: "18px",
                      fontWeight: 600,
                      textDecoration: "none",
                      display: "block",
                      flex: 1,
                    }}
                  >
                    {cluster.headline}
                  </a>
                  {cluster.region && (
                    <span style={{ 
                      fontSize: "12px", 
                      padding: "4px 8px", 
                      background: "#e5f0f9", 
                      color: "#0f3d5d", 
                      borderRadius: "12px",
                      marginLeft: "12px"
                    }}>
                      {cluster.region}
                    </span>
                  )}
                </div>
                
                {cluster.summary && (
                  <p style={{ margin: "8px 0", color: "#4e6475", fontSize: "14px", lineHeight: 1.5 }}>
                    {cluster.summary}
                  </p>
                )}

                <div style={{ display: "flex", gap: "16px", marginTop: "12px", alignItems: "center", flexWrap: "wrap" }}>
                  <span style={{ color: "#607586", fontSize: "13px" }}>
                    {formatClusterDate(cluster.publish_date ?? "")}
                  </span>
                  
                  <span style={{ color: "#607586", fontSize: "13px" }}>
                    • {cluster.source_count || 0} source{(cluster.source_count || 0) !== 1 ? 's' : ''}
                  </span>

                  {cluster.topic_tags && cluster.topic_tags.length > 0 && (
                    <div style={{ display: "flex", gap: "6px", marginLeft: "auto" }}>
                      {cluster.topic_tags.map(tag => (
                        <span key={tag} style={{ 
                          fontSize: "11px", 
                          padding: "2px 8px", 
                          border: "1px solid #d8e4ee",
                          color: "#607586", 
                          borderRadius: "4px"
                        }}>
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </li>
            ))}
            
            {data.items.length === 0 && (
              <div style={{ padding: "40px", textAlign: "center", color: "#607586" }}>
                No clusters found for the selected filters.
              </div>
            )}
          </ul>
        </section>
      </div>
    </main>
  );
}
