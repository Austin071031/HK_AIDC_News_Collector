import { getClusters } from "../lib/api";
import { formatClusterDate } from "../lib/format";

export default async function HomePage() {
  const data = await getClusters();

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
            <span style={{ color: "#4e6475", fontSize: "14px" }}>
              {data.items.length} items
            </span>
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
                <a
                  href={`/clusters/${cluster.cluster_id}`}
                  style={{
                    color: "#0f3d5d",
                    fontSize: "18px",
                    fontWeight: 600,
                    textDecoration: "none",
                  }}
                >
                  {cluster.headline}
                </a>
                <p style={{ margin: "10px 0 0", color: "#607586" }}>
                  {formatClusterDate(cluster.publish_date ?? "")}
                </p>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  );
}
