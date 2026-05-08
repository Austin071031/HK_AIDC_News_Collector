"use client";

import { useState } from "react";
import { submitArticleAction } from "../lib/api";
import { ArticleAction } from "../lib/types";

type ActionPanelProps = {
  articleId: string;
  initialAction?: ArticleAction | null;
};

export default function AnalystActionPanel({ articleId, initialAction }: ActionPanelProps) {
  const [isHidden, setIsHidden] = useState(initialAction?.is_hidden || false);
  const [isFavorite, setIsFavorite] = useState(initialAction?.is_favorite || false);
  const [notes, setNotes] = useState(initialAction?.notes || "");
  const [tags, setTags] = useState(initialAction?.tags || "");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      const tagsArray = tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      await submitArticleAction(articleId, {
        is_hidden: isHidden,
        is_favorite: isFavorite,
        notes: notes || null,
        tags: tagsArray.length > 0 ? tagsArray.join(",") : null,
      });
      setMessage("Saved successfully!");
    } catch (error) {
      setMessage("Failed to save actions.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section
      style={{
        padding: "32px",
        borderRadius: "24px",
        background: "#ffffff",
        boxShadow: "0 24px 60px rgba(12, 36, 53, 0.12)",
      }}
    >
      <h2 style={{ margin: "0 0 20px", fontSize: "24px" }}>Analyst Actions</h2>

      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={isHidden}
              onChange={(e) => setIsHidden(e.target.checked)}
            />
            Hide Cluster
          </label>

          <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={isFavorite}
              onChange={(e) => setIsFavorite(e.target.checked)}
            />
            Favorite
          </label>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "8px", fontSize: "14px", fontWeight: 500 }}>
            Manual Tags (comma separated)
          </label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="e.g., urgent, review, Q3_priority"
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: "8px",
              border: "1px solid #d8e4ee",
              fontSize: "14px",
            }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "8px", fontSize: "14px", fontWeight: 500 }}>
            Analyst Notes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add your research notes here..."
            rows={4}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: "8px",
              border: "1px solid #d8e4ee",
              fontSize: "14px",
              resize: "vertical",
            }}
          />
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "16px", marginTop: "8px" }}>
          <button
            onClick={handleSave}
            disabled={saving}
            style={{
              padding: "10px 24px",
              borderRadius: "8px",
              background: "#0f3d5d",
              color: "#fff",
              border: "none",
              cursor: saving ? "not-allowed" : "pointer",
              fontWeight: 500,
              fontSize: "14px",
            }}
          >
            {saving ? "Saving..." : "Save Actions"}
          </button>
          {message && (
            <span style={{ fontSize: "14px", color: message.includes("Failed") ? "#e74c3c" : "#2ecc71" }}>
              {message}
            </span>
          )}
        </div>
      </div>
    </section>
  );
}