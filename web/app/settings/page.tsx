"use client";

import { useEffect, useState } from "react";
import { getSources, createSource, deleteSource, getKeywords, createKeyword, deleteKeyword } from "../../lib/api";
import type { Source, Keyword } from "../../lib/types";

export default function SettingsPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  
  // Forms
  const [newSourceName, setNewSourceName] = useState("");
  const [newSourceUrl, setNewSourceUrl] = useState("");
  const [newSourceMode, setNewSourceMode] = useState("search");
  const [newKeyword, setNewKeyword] = useState("");

  const loadData = async () => {
    try {
      const [srcs, kwds] = await Promise.all([getSources(), getKeywords()]);
      setSources(srcs);
      setKeywords(kwds);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    await createSource({
      name: newSourceName,
      base_url: newSourceUrl,
      region: "global",
      language: "en",
      source_type: "media",
      discovery_mode: newSourceMode,
      priority: 1,
      active: true
    });
    setNewSourceName("");
    setNewSourceUrl("");
    loadData();
  };

  const handleAddKeyword = async (e: React.FormEvent) => {
    e.preventDefault();
    await createKeyword({ keyword: newKeyword, active: true });
    setNewKeyword("");
    loadData();
  };

  return (
    <main style={{ padding: "48px 24px", color: "#08131a" }}>
      <h1 style={{ fontSize: "32px", marginBottom: "24px" }}>Settings / Configuration</h1>
      
      <div style={{ display: "flex", gap: "32px" }}>
        {/* Sources Section */}
        <section style={{ flex: 2, background: "#fff", padding: "24px", borderRadius: "12px", boxShadow: "0 12px 40px rgba(0,0,0,0.08)" }}>
          <h2>Sources</h2>
          <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse", marginBottom: "24px" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #ccc" }}>
                <th style={{ padding: "8px" }}>Name</th>
                <th style={{ padding: "8px" }}>Mode</th>
                <th style={{ padding: "8px" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {sources.map(s => (
                <tr key={s.id} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: "8px" }}>{s.name}</td>
                  <td style={{ padding: "8px" }}>{s.discovery_mode}</td>
                  <td style={{ padding: "8px" }}>
                    <button onClick={async () => { await deleteSource(s.id); loadData(); }} style={{ color: "red", cursor: "pointer", background: "none", border: "none" }}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <form onSubmit={handleAddSource} style={{ display: "flex", gap: "8px" }}>
            <input required placeholder="Name" value={newSourceName} onChange={e => setNewSourceName(e.target.value)} style={{ padding: "8px", border: "1px solid #ccc", borderRadius: "4px" }} />
            <input required placeholder="Base URL" value={newSourceUrl} onChange={e => setNewSourceUrl(e.target.value)} style={{ padding: "8px", border: "1px solid #ccc", borderRadius: "4px" }} />
            <select value={newSourceMode} onChange={e => setNewSourceMode(e.target.value)} style={{ padding: "8px", border: "1px solid #ccc", borderRadius: "4px" }}>
              <option value="search">Search</option>
              <option value="rss">RSS</option>
            </select>
            <button type="submit" style={{ padding: "8px 16px", background: "#0f3d5d", color: "#fff", border: "none", borderRadius: "4px" }}>Add Source</button>
          </form>
        </section>

        {/* Keywords Section */}
        <section style={{ flex: 1, background: "#fff", padding: "24px", borderRadius: "12px", boxShadow: "0 12px 40px rgba(0,0,0,0.08)" }}>
          <h2>Keywords</h2>
          <ul style={{ listStyle: "none", padding: 0, marginBottom: "24px" }}>
            {keywords.map(k => (
              <li key={k.id} style={{ display: "flex", justifyContent: "space-between", padding: "8px", borderBottom: "1px solid #eee" }}>
                <span>{k.keyword}</span>
                <button onClick={async () => { await deleteKeyword(k.id); loadData(); }} style={{ color: "red", cursor: "pointer", background: "none", border: "none" }}>Delete</button>
              </li>
            ))}
          </ul>
          
          <form onSubmit={handleAddKeyword} style={{ display: "flex", gap: "8px" }}>
            <input required placeholder="New keyword" value={newKeyword} onChange={e => setNewKeyword(e.target.value)} style={{ padding: "8px", border: "1px solid #ccc", borderRadius: "4px", flex: 1 }} />
            <button type="submit" style={{ padding: "8px 16px", background: "#0f3d5d", color: "#fff", border: "none", borderRadius: "4px" }}>Add</button>
          </form>
        </section>
      </div>
    </main>
  );
}
