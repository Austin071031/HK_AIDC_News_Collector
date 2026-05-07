"use client";

import { useState, useEffect } from "react";
import { getClusterDetail } from "../lib/api";
import { formatClusterDate } from "../lib/format";
import AnalystActionPanel from "./clusters/[clusterId]/AnalystActionPanel";
import type { ClusterDetailResponse } from "../lib/types";

export default function SplitViewDashboard({ initialClusters }: { initialClusters: any[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ClusterDetailResponse | null>(null);

  useEffect(() => {
    if (selectedId) {
      getClusterDetail(selectedId).then(setDetail).catch(console.error);
    } else {
      setDetail(null);
    }
  }, [selectedId]);

  return (
    <div style={{ display: "flex", gap: "24px", height: "calc(100vh - 250px)" }}>
      {/* Left Pane: Feed */}
      <div style={{ flex: 1, overflowY: "auto", paddingRight: "12px", borderRight: "1px solid #d8e4ee" }}>
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: "12px" }}>
          {initialClusters.map((cluster) => (
            <li
              key={cluster.cluster_id}
              onClick={() => setSelectedId(cluster.cluster_id)}
              style={{
                padding: "16px",
                borderRadius: "12px",
                border: selectedId === cluster.cluster_id ? "2px solid #0f3d5d" : "1px solid #d8e4ee",
                background: selectedId === cluster.cluster_id ? "#e5f0f9" : "#f8fbfd",
                cursor: "pointer",
                transition: "all 0.2s"
              }}
            >
              <div style={{ fontWeight: 600, color: "#0f3d5d", marginBottom: "8px" }}>
                {cluster.headline}
              </div>
              <div style={{ fontSize: "12px", color: "#607586" }}>
                {formatClusterDate(cluster.publish_date ?? "")} • {cluster.region}
              </div>
            </li>
          ))}
          {initialClusters.length === 0 && (
            <div style={{ padding: "20px", textAlign: "center", color: "#607586" }}>No clusters found.</div>
          )}
        </ul>
      </div>

      {/* Right Pane: Details */}
      <div style={{ flex: 2, overflowY: "auto", paddingLeft: "12px" }}>
        {!selectedId && (
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "#8da2b3" }}>
            Select a cluster to view details
          </div>
        )}
        
        {selectedId && !detail && (
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "#8da2b3" }}>
            Loading details...
          </div>
        )}

        {detail && (
          <div>
            <h2 style={{ fontSize: "24px", color: "#0f3d5d", marginTop: 0 }}>{detail.headline}</h2>
            
            <div style={{ background: "#f8fbfd", padding: "16px", borderRadius: "12px", border: "1px solid #d8e4ee", marginBottom: "20px" }}>
              <h3 style={{ margin: "0 0 8px", fontSize: "12px", textTransform: "uppercase", color: "#547086" }}>AI Summary</h3>
              <p style={{ margin: 0, color: "#0f3d5d", lineHeight: 1.6 }}>{detail.rationale}</p>
            </div>

            <AnalystActionPanel clusterId={detail.id.toString()} />

            <h3 style={{ fontSize: "18px", marginTop: "32px", marginBottom: "16px" }}>Sources ({detail.articles.length})</h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: "12px" }}>
              {detail.articles.map(article => (
                <li key={article.id} style={{ padding: "12px", border: "1px solid #d8e4ee", borderRadius: "8px" }}>
                  <a href={article.url} target="_blank" rel="noreferrer" style={{ fontSize: "14px", color: "#0f3d5d", textDecoration: "none", fontWeight: 500 }}>
                    {article.title}
                  </a>
                  <div style={{ fontSize: "12px", color: "#607586", marginTop: "4px" }}>{article.source_name}</div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
