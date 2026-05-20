"use client";

import { useState, useEffect } from "react";
import type { SourceArticle } from "../lib/types";
import { getArticleContent } from "../lib/api";

export default function SplitViewDashboard({ initialArticles }: { initialArticles: SourceArticle[] }) {
  const [selectedUrl, setSelectedUrl] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [articleHtml, setArticleHtml] = useState<string | null>(null);
  const [isLoadingContent, setIsLoadingContent] = useState<boolean>(false);

  useEffect(() => {
    if (selectedId && selectedUrl) {
      setIsLoadingContent(true);
      setArticleHtml(null);
      getArticleContent(selectedId)
        .then((content) => {
          if (content.raw_html) {
            try {
              const origin = new URL(selectedUrl).origin;
              const injectedHtml = content.raw_html.replace(
                /<head>/i, 
                `<head><base href="${origin}/">`
              );
              setArticleHtml(injectedHtml);
            } catch (e) {
              setArticleHtml(content.raw_html);
            }
          } else if (content.raw_text) {
            setArticleHtml(
              `<div style="padding: 24px; font-family: system-ui, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto;">
                <h2>Article Content</h2>
                <pre style="white-space: pre-wrap; font-family: inherit;">${content.raw_text}</pre>
              </div>`
            );
          } else {
            setArticleHtml(`<div style="padding: 40px; font-family: sans-serif; color: #8da2b3;">No content available for this article.</div>`);
          }
        })
        .catch((err) => {
          console.error(err);
          setArticleHtml(`<div style="padding: 40px; font-family: sans-serif; color: #d9534f;">Failed to load article content. It may have been deleted or is unavailable.</div>`);
        })
        .finally(() => {
          setIsLoadingContent(false);
        });
    }
  }, [selectedId, selectedUrl]);

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
                   setSelectedUrl(article.url);
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
                 <h3 style={{ margin: "0 0 12px 0", fontSize: "16px", color: "#0f3d5d", lineHeight: "1.4" }}>
                   {article.title}
                 </h3>
                 
                 <div style={{ background: selectedId === article.id ? "#d3e4f3" : "#f8fbfd", padding: "12px", borderRadius: "8px", border: "1px solid #e1ebf2" }}>
                   <h4 style={{ margin: "0 0 4px 0", fontSize: "11px", textTransform: "uppercase", color: "#547086" }}>AI Summary</h4>
                   <p style={{ margin: 0, color: "#2d4456", fontSize: "13px", lineHeight: 1.5 }}>
                     {article.enrichment
                       ? (article.enrichment.summary || `No summary generated (${article.enrichment.relevance})`)
                       : "Summary pending..."}
                   </p>
                 </div>
               </div>
             ))
          )}
        </div>
      </div>

      {/* Right Pane: Iframe Viewer */}
      <div style={{ flex: 2, overflowY: "hidden", display: "flex", flexDirection: "column" }}>
        {!selectedUrl && (
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "#8da2b3", border: "1px dashed #d8e4ee", borderRadius: "12px" }}>
            Select an article to view the website
          </div>
        )}
        
        {selectedUrl && (
          <div style={{ height: "100%", border: "1px solid #d8e4ee", borderRadius: "12px", overflow: "hidden", background: "#fff", display: "flex", flexDirection: "column", position: "relative" }}>
            <div style={{ padding: "12px", background: "#f8fbfd", borderBottom: "1px solid #d8e4ee", display: "flex", justifyContent: "space-between", alignItems: "center", zIndex: 10 }}>
              <span style={{ fontSize: "13px", color: "#547086", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", marginRight: "16px" }}>
                {selectedUrl}
              </span>
              <a href={selectedUrl} target="_blank" rel="noreferrer" style={{ fontSize: "13px", color: "#0f3d5d", textDecoration: "none", fontWeight: "bold", whiteSpace: "nowrap" }}>
                Open in new tab ↗
              </a>
            </div>
            {isLoadingContent && (
              <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(255,255,255,0.8)", zIndex: 5 }}>
                <span style={{ color: "#0f3d5d", fontWeight: "bold" }}>Loading content...</span>
              </div>
            )}
            <iframe 
              srcDoc={articleHtml || undefined} 
              style={{ width: "100%", height: "100%", border: "none", flexGrow: 1 }} 
              title="Article Viewer"
              sandbox="allow-same-origin allow-popups allow-forms"
            />
          </div>
        )}
      </div>
    </div>
  );
}
