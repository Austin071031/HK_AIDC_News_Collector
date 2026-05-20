"use client";

import { useState } from "react";
import { cleanupDatabase } from "../lib/api";

export default function CleanupButton() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleCleanup = async () => {
    if (!window.confirm("Are you sure you want to clean up all news content? This will delete all articles, clusters, and raw documents but leave sources and keywords intact.")) {
      return;
    }

    setLoading(true);
    setMessage(null);
    try {
      await cleanupDatabase();
      setMessage("Database cleaned up!");
      setTimeout(() => setMessage(null), 3000);
      
      // Optional: reload the page to refresh data
      window.location.reload();
    } catch (err: any) {
      console.error(err);
      setMessage("Failed to clean up");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: "auto", paddingTop: "32px" }}>
      <button
        onClick={handleCleanup}
        disabled={loading}
        style={{
          width: "100%",
          padding: "10px",
          background: loading ? "#555" : "#e03131",
          color: "white",
          border: "none",
          borderRadius: "8px",
          cursor: loading ? "not-allowed" : "pointer",
          fontSize: "14px",
          fontWeight: "bold",
          transition: "background 0.2s"
        }}
        onMouseOver={(e) => {
          if (!loading) e.currentTarget.style.background = "#c92a2a";
        }}
        onMouseOut={(e) => {
          if (!loading) e.currentTarget.style.background = "#e03131";
        }}
      >
        {loading ? "Cleaning..." : "Clean Up Content"}
      </button>
      {message && (
        <p style={{ color: message.includes("Failed") ? "#ff6b6b" : "#69db7c", fontSize: "12px", marginTop: "8px", textAlign: "center" }}>
          {message}
        </p>
      )}
    </div>
  );
}
