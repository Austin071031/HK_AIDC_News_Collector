import { Suspense } from "react";
import { getArticles } from "../lib/api";
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
  const articles = await getArticles(resolvedParams);

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
          maxWidth: "1400px",
          margin: "0 auto",
          display: "grid",
          gap: "24px",
        }}
      >
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
            <h2 style={{ margin: 0, fontSize: "24px" }}>News Feed</h2>
          </div>

          <Suspense fallback={<div style={{ textAlign: "center", padding: "40px" }}>Loading dashboard...</div>}>
            <SplitViewDashboard initialArticles={articles} />
          </Suspense>
        </section>
      </div>
    </main>
  );
}
