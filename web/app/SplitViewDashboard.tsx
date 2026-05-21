"use client";

import { useState } from "react";
import type { SourceArticle } from "../lib/types";

export default function SplitViewDashboard({ initialArticles }: { initialArticles: SourceArticle[] }) {
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const selectedArticle = initialArticles.find(a => a.id === selectedId);

  return (
    <div style={{ display: "flex", gap: "24px", height: "calc(100vh - 250px)" }}>
      {/* Left Pane: Article Cards */}
      <div style={{ flex: 1, overflowY: "auto", paddingRight: "12px", borderRight: "1px solid #d8e4ee" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {initialArticles.length === 0 ? (
             <div style={{ textAlign: "center", color: "#8da2b3", marginTop: "40px" }}>No articles found.</div>
          ) : (
             initialArticles.map(article => (
               <div 
                 key={article.id} 
                 onClick={() => {
                   setSelectedId(article.id);
                 }}
                 style={{ 
                   border: selectedId === article.id ? "2px solid #0f3d5d" : "1px solid #d8e4ee", 
                   borderRadius: "12px", 
                   padding: "16px", 
                   background: selectedId === article.id ? "#e5f0f9" : "#fff",
                   cursor: "pointer",
                   transition: "all 0.2s"
                 }}
               >
                 <div style={{ fontSize: "12px", color: "#607586", marginBottom: "8px", fontWeight: "bold", textTransform: "uppercase" }}>
                    {article.source_name} • {article.published_at ? new Date(article.published_at).toLocaleDateString() : "Unknown Date"}
                  </div>
                 <h3 style={{ margin: "0", fontSize: "16px", color: "#0f3d5d", lineHeight: "1.4" }}>
                   {article.title}
                 </h3>
               </div>
             ))
          )}
        </div>
      </div>

      {/* Right Pane: LLM Content Viewer */}
      <div style={{ flex: 2, overflowY: "hidden", display: "flex", flexDirection: "column" }}>
        {!selectedArticle && (
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "#8da2b3", border: "1px dashed #d8e4ee", borderRadius: "12px" }}>
            Select an article to view the LLM extraction
          </div>
        )}
        
        {selectedArticle && (
          <div style={{ height: "100%", border: "1px solid #d8e4ee", borderRadius: "12px", overflowY: "auto", background: "#fff", display: "flex", flexDirection: "column", position: "relative" }}>
            <div style={{ padding: "16px", background: "#f8fbfd", borderBottom: "1px solid #d8e4ee", display: "flex", justifyContent: "space-between", alignItems: "center", position: "sticky", top: 0, zIndex: 10 }}>
              <span style={{ fontSize: "14px", fontWeight: "bold", color: "#0f3d5d", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", marginRight: "16px" }}>
                AI Analysis & Extraction
              </span>
              <a href={selectedArticle.url} target="_blank" rel="noreferrer" style={{ fontSize: "13px", color: "#fff", background: "#0f3d5d", padding: "6px 16px", borderRadius: "6px", textDecoration: "none", fontWeight: "bold", whiteSpace: "nowrap", transition: "background 0.2s" }} onMouseOver={e => e.currentTarget.style.background = '#1a5885'} onMouseOut={e => e.currentTarget.style.background = '#0f3d5d'}>
                Read Original Article ↗
              </a>
            </div>
            
            <div style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "32px" }}>
              {/* Summary Section */}
              <section>
                <h2 style={{ fontSize: "18px", color: "#0f3d5d", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "20px" }}>📝</span> Summary
                </h2>
                <div style={{ color: "#2d4456", fontSize: "15px", lineHeight: "1.6", background: "#f8fbfd", padding: "16px", borderRadius: "8px", border: "1px solid #e1ebf2" }}>
                  {selectedArticle.enrichment?.summary || "No summary available."}
                </div>
              </section>

              {/* Key Points Section */}
              <section>
                <h2 style={{ fontSize: "18px", color: "#0f3d5d", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "20px" }}>💡</span> Key Points
                </h2>
                <div style={{ color: "#2d4456", fontSize: "15px", lineHeight: "1.6" }}>
                  {selectedArticle.enrichment?.key_points && selectedArticle.enrichment.key_points.length > 0 ? (
                    <ul style={{ margin: 0, paddingLeft: "24px", display: "flex", flexDirection: "column", gap: "8px" }}>
                      {selectedArticle.enrichment.key_points.map((point, idx) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  ) : (
                    <div style={{ color: "#8da2b3", fontStyle: "italic" }}>No key points extracted.</div>
                  )}
                </div>
              </section>

              {/* Extracted Content Section */}
              <section>
                <h2 style={{ fontSize: "18px", color: "#0f3d5d", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "20px" }}>📄</span> Extracted Content
                </h2>
                <div style={{ color: "#2d4456", fontSize: "15px", lineHeight: "1.8", whiteSpace: "pre-wrap" }}>
                  {selectedArticle.enrichment?.extracted_content || (
                    <span style={{ color: "#8da2b3", fontStyle: "italic" }}>No extracted content available.</span>
                  )}
                </div>
              </section>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
