"use client";

import { useEffect, useState } from "react";
import { getSources, createSource, updateSource, deleteSource, getKeywords, createKeyword, deleteKeyword, getConfig, updateConfig } from "../../lib/api";
import type { Source, Keyword } from "../../lib/types";

export default function SettingsPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [llmPrompt, setLlmPrompt] = useState("");
  const [savingPrompt, setSavingPrompt] = useState(false);
  
  // Forms
  const [newSourceName, setNewSourceName] = useState("");
  const [newSourceUrl, setNewSourceUrl] = useState("");
  const [newSourceMode, setNewSourceMode] = useState("search");
  const [newKeyword, setNewKeyword] = useState("");

  // Edit State
  const [editingSourceId, setEditingSourceId] = useState<number | null>(null);
  const [editSourceData, setEditSourceData] = useState<Partial<Source>>({});

  const loadData = async () => {
    try {
      const [srcs, kwds] = await Promise.all([getSources(), getKeywords()]);
      setSources(srcs);
      setKeywords(kwds);
      
      try {
        const config = await getConfig("llm_filter_prompt");
        if (config && config.value) {
          setLlmPrompt(config.value);
        }
      } catch (err) {
        console.warn("Could not load LLM prompt config");
      }
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

  const handleUpdateSource = async (id: number) => {
    await updateSource(id, editSourceData);
    setEditingSourceId(null);
    loadData();
  };

  const handleAddKeyword = async (e: React.FormEvent) => {
    e.preventDefault();
    await createKeyword({ keyword: newKeyword, active: true });
    setNewKeyword("");
    loadData();
  };

  const handleSavePrompt = async () => {
    setSavingPrompt(true);
    try {
      await updateConfig("llm_filter_prompt", llmPrompt);
      alert("LLM Filter Prompt saved successfully!");
    } catch (e) {
      alert("Failed to save LLM Filter Prompt.");
    }
    setSavingPrompt(false);
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
                <th style={{ padding: "8px" }}>Base URL</th>
                <th style={{ padding: "8px" }}>Mode</th>
                <th style={{ padding: "8px" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {sources.map(s => (
                <tr key={s.id} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: "8px" }}>
                    {editingSourceId === s.id ? (
                      <input 
                        value={editSourceData.name || ""} 
                        onChange={e => setEditSourceData({...editSourceData, name: e.target.value})} 
                        style={{ padding: "4px", width: "100%" }}
                      />
                    ) : (
                      s.name
                    )}
                  </td>
                  <td style={{ padding: "8px" }}>
                    {editingSourceId === s.id ? (
                      <input 
                        value={editSourceData.base_url || ""} 
                        onChange={e => setEditSourceData({...editSourceData, base_url: e.target.value})} 
                        style={{ padding: "4px", width: "100%" }}
                      />
                    ) : (
                      s.base_url
                    )}
                  </td>
                  <td style={{ padding: "8px" }}>
                    {editingSourceId === s.id ? (
                      <select 
                        value={editSourceData.discovery_mode || "search"} 
                        onChange={e => setEditSourceData({...editSourceData, discovery_mode: e.target.value})}
                        style={{ padding: "4px" }}
                      >
                        <option value="search">Search</option>
                        <option value="rss">RSS</option>
                      </select>
                    ) : (
                      s.discovery_mode
                    )}
                  </td>
                  <td style={{ padding: "8px", display: "flex", gap: "8px" }}>
                    {editingSourceId === s.id ? (
                      <>
                        <button onClick={() => handleUpdateSource(s.id)} style={{ color: "green", cursor: "pointer", background: "none", border: "none" }}>Save</button>
                        <button onClick={() => setEditingSourceId(null)} style={{ color: "gray", cursor: "pointer", background: "none", border: "none" }}>Cancel</button>
                      </>
                    ) : (
                      <>
                        <button onClick={() => { setEditingSourceId(s.id); setEditSourceData(s); }} style={{ color: "blue", cursor: "pointer", background: "none", border: "none" }}>Edit</button>
                        <button onClick={async () => { await deleteSource(s.id); loadData(); }} style={{ color: "red", cursor: "pointer", background: "none", border: "none" }}>Delete</button>
                      </>
                    )}
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
            <button type="submit" style={{ padding: "8px 16px", background: "#0f3d5d", color: "#fff", border: "none", borderRadius: "4px", whiteSpace: "nowrap" }}>Add Source</button>
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

      {/* LLM Filter Config Section */}
      <section style={{ background: "#fff", padding: "24px", borderRadius: "12px", boxShadow: "0 12px 40px rgba(0,0,0,0.08)", marginTop: "32px" }}>
        <h2>LLM Filter Configuration</h2>
        <p style={{ color: "#64748b", marginBottom: "16px", fontSize: "14px" }}>
          This prompt is used to evaluate the scraped text of every discovered article. If the LLM replies "NO", the article is dropped.
        </p>
        <textarea 
          value={llmPrompt}
          onChange={e => setLlmPrompt(e.target.value)}
          rows={4}
          style={{ width: "100%", padding: "12px", border: "1px solid #ccc", borderRadius: "8px", fontFamily: "inherit", marginBottom: "16px", resize: "vertical" }}
        />
        <button 
          onClick={handleSavePrompt}
          disabled={savingPrompt}
          style={{ padding: "10px 20px", background: savingPrompt ? "#94a3b8" : "#0f3d5d", color: "#fff", border: "none", borderRadius: "8px", cursor: savingPrompt ? "not-allowed" : "pointer", fontWeight: 600 }}
        >
          {savingPrompt ? "Saving..." : "Save Prompt"}
        </button>
      </section>
    </main>
  );
}
