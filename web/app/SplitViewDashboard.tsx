"use client";

import { useState, useEffect } from "react";
import { getSourceArticles } from "../lib/api";
import AnalystActionPanel from "../components/AnalystActionPanel";
import type { SourceWithCount, SourceArticle } from "../lib/types";

export default function SplitViewDashboard({ initialSources }: { initialSources: SourceWithCount[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [articles, setArticles] = useState<SourceArticle[] | null>(null);

  useEffect(() => {
    if (selectedId) {
      setArticles(null); // Reset while loading
      getSourceArticles(selectedId).then(setArticles).catch(console.error);
    } else {
      setArticles(null);
    }
  }, [selectedId]);

  return (
    <div style={{ display: "flex", gap: "24px", height: "calc(100vh - 250px)" }}>
      {/* Left Pane: Sources List */}
      <div style={{ flex: 1, overflowY: "auto", paddingRight: "12px", borderRight: "1px solid #d8e4ee" }}>
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: "12px" }}>
          {initialSources.map((source) => (
            <li
              key={source.id}
              onClick={() => setSelectedId(source.id.toString())}
              style={{
                padding: "16px",
                borderRadius: "12px",
                border: selectedId === source.id.toString() ? "2px solid #0f3d5d" : "1px solid #d8e4ee",
                background: selectedId === source.id.toString() ? "#e5f0f9" : "#f8fbfd",
                cursor: "pointer",
                transition: "all 0.2s"
              }}
            >
              <div style={{ fontWeight: 600, color: "#0f3d5d", marginBottom: "4px" }}>
                {source.name}
              </div>
              <div style={{ fontSize: "12px", color: "#607586" }}>
                {source.region} • {source.article_count || 0} articles
              </div>
            </li>
          ))}
          {initialSources.length === 0 && (
            <div style={{ padding: "20px", textAlign: "center", color: "#607586" }}>No sources found.</div>
          )}
        </ul>
      </div>

      {/* Right Pane: Article Cards */}
      <div style={{ flex: 2, overflowY: "auto", paddingLeft: "12px" }}>
        {!selectedId && (
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "#8da2b3" }}>
            Select a source to view articles
          </div>
        )}
        
        {selectedId && !articles && (
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "#8da2b3" }}>
            Loading articles...
          </div>
        )}

        {articles && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {articles.length === 0 ? (
               <div style={{ textAlign: "center", color: "#8da2b3", marginTop: "40px" }}>No articles found for this source.</div>
            ) : (
               articles.map(article => (
                 <div key={article.id} style={{ border: "1px solid #d8e4ee", borderRadius: "12px", padding: "20px", background: "#fff" }}>
                   <h3 style={{ margin: "0 0 12px 0", fontSize: "20px", color: "#0f3d5d" }}>
                     <a href={article.url} target="_blank" rel="noreferrer" style={{ textDecoration: "none", color: "inherit" }}>
                       {article.title}
                     </a>
                   </h3>
                   
                   <div style={{ background: "#f8fbfd", padding: "12px", borderRadius: "8px", border: "1px solid #e1ebf2", marginBottom: "16px" }}>
                     <h4 style={{ margin: "0 0 4px 0", fontSize: "11px", textTransform: "uppercase", color: "#547086" }}>AI Summary</h4>
                     <p style={{ margin: 0, color: "#2d4456", fontSize: "14px", lineHeight: 1.5 }}>
                       {article.enrichment?.summary || "Summary pending..."}
                     </p>
                   </div>

                   <AnalystActionPanel articleId={article.id.toString()} initialAction={article.action} />
                 </div>
               ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
