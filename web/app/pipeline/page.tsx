"use client";
import { useState, useEffect, useRef } from "react";

export default function PipelinePage() {
  const [logs, setLogs] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const handleRunPipeline = async (type: "rss" | "search") => {
    setIsRunning(true);
    setLogs((prev) => [...prev, `> Starting ${type.toUpperCase()} Pipeline...`]);
    try {
      await fetch(`http://localhost:8000/api/jobs/run-${type}-pipeline`, { method: "POST" });
      
      const eventSource = new EventSource("http://localhost:8000/api/jobs/stream");
      eventSource.onmessage = (event) => {
        setLogs((prev) => [...prev, event.data]);
        if (event.data.includes("Daily pipeline task completed successfully") || event.data.includes("Error in daily pipeline task")) {
          setIsRunning(false);
          eventSource.close();
        }
      };
      eventSource.onerror = () => {
        setIsRunning(false);
        eventSource.close();
      };
    } catch (e) {
      setLogs((prev) => [...prev, "> Failed to trigger pipeline."]);
      setIsRunning(false);
    }
  };

  return (
    <main style={{ padding: "48px", maxWidth: "960px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "32px", color: "#08131a", marginBottom: "24px" }}>Pipeline Manager</h1>
      
      <section style={{ background: "#fff", padding: "24px", borderRadius: "16px", boxShadow: "0 12px 32px rgba(0,0,0,0.05)", marginBottom: "32px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <h2 style={{ margin: 0, fontSize: "20px" }}>Execution Control</h2>
          <div style={{ display: "flex", gap: "12px" }}>
            <button 
              onClick={() => handleRunPipeline("rss")}
              disabled={isRunning}
              style={{ 
                padding: "10px 20px", 
                background: isRunning ? "#94a3b8" : "#10b981", 
                color: "#fff", 
                border: "none", 
                borderRadius: "8px", 
                cursor: isRunning ? "not-allowed" : "pointer",
                fontWeight: 600
              }}
            >
              {isRunning ? "Running..." : "▶ Run RSS Pipeline"}
            </button>
            <button 
              onClick={() => handleRunPipeline("search")}
              disabled={isRunning}
              style={{ 
                padding: "10px 20px", 
                background: isRunning ? "#94a3b8" : "#0ea5e9", 
                color: "#fff", 
                border: "none", 
                borderRadius: "8px", 
                cursor: isRunning ? "not-allowed" : "pointer",
                fontWeight: 600
              }}
            >
              {isRunning ? "Running..." : "▶ Run Search Pipeline"}
            </button>
          </div>
        </div>
        
        <div style={{ background: "#1e293b", color: "#a1a1aa", fontFamily: "monospace", padding: "16px", borderRadius: "8px", height: "300px", overflowY: "auto", fontSize: "13px", lineHeight: "1.6" }}>
          {logs.length === 0 ? (
            <span style={{ color: "#475569" }}>Ready to run. Logs will appear here...</span>
          ) : (
            logs.map((log, i) => <div key={i}>{log}</div>)
          )}
          <div ref={logsEndRef} />
        </div>
      </section>
      
      <div style={{ color: "#64748b", fontSize: "14px", marginTop: "40px" }}>
        Note: Source and Keyword Management UI can be added below this section in future iterations, relying on the CRUD APIs created in Task 2.
      </div>
    </main>
  );
}
