import { getClusters } from "../lib/api";
import SplitViewDashboard from "./SplitViewDashboard";

type SearchParams = {
  region?: string;
  relevance?: string;
  start_date?: string;
  end_date?: string;
  topic_tag?: string;
  analyst_status?: string;
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
        minHeight: "100%",
        padding: "48px 24px",
        background:
          "linear-gradient(180deg, #06131d 0%, #0d2131 55%, #f3f7fb 55%, #f3f7fb 100%)",
        color: "#08131a",
      }}
    >
      <div
        style={{
          maxWidth: "1200px",
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
            <form method="get" style={{ display: "flex", flexWrap: "wrap", gap: "12px", justifyContent: "flex-end", maxWidth: "600px" }}>
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
                <option value="adjacent">Adjacent</option>
              </select>
              <select 
                name="analyst_status" 
                defaultValue={resolvedParams.analyst_status || ""}
                style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #d8e4ee" }}
              >
                <option value="">All Status</option>
                <option value="unread">Unread</option>
                <option value="favorite">Favorite</option>
                <option value="hidden">Hidden</option>
              </select>
              <input
                type="text"
                name="topic_tag"
                placeholder="Filter by Topic..."
                defaultValue={resolvedParams.topic_tag || ""}
                style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #d8e4ee", width: "140px" }}
              />
              <input
                type="date"
                name="start_date"
                defaultValue={resolvedParams.start_date || ""}
                style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #d8e4ee" }}
              />
              <input
                type="date"
                name="end_date"
                defaultValue={resolvedParams.end_date || ""}
                style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #d8e4ee" }}
              />
              <button 
                type="submit"
                style={{ padding: "6px 16px", borderRadius: "6px", background: "#0f3d5d", color: "#fff", border: "none", cursor: "pointer" }}
              >
                Filter
              </button>
            </form>
          </div>

          <SplitViewDashboard initialClusters={data.items} />
        </section>
      </div>
    </main>
  );
}
