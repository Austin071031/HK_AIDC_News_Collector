"use client";

import { useState } from "react";
import Link from "next/link";
import CleanupButton from "./CleanupButton";

export default function SidebarLayout({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ display: "flex", minHeight: "100vh", width: "100%" }}>
      {/* Sidebar */}
      <aside 
        style={{ 
          width: isOpen ? "240px" : "0px", 
          background: "#06131d", 
          color: "#f7fbff", 
          flexShrink: 0, 
          display: "flex", 
          flexDirection: "column",
          transition: "width 0.3s ease, padding 0.3s ease",
          overflow: "hidden",
          padding: isOpen ? "24px" : "24px 0",
          position: "relative"
        }}
      >
        <div style={{ width: "240px", padding: "0 24px", boxSizing: "border-box", display: "flex", flexDirection: "column", height: "100%", opacity: isOpen ? 1 : 0, transition: "opacity 0.2s ease" }}>
          <h2 style={{ fontSize: "18px", color: "#8fd3ff", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "32px", whiteSpace: "nowrap" }}>HK AIDC Collector</h2>
          <nav style={{ display: "flex", flexDirection: "column", gap: "16px", flexGrow: 1 }}>
            <Link href="/" style={{ color: "#d6e7f5", textDecoration: "none", fontSize: "16px", padding: "8px 12px", borderRadius: "8px", display: "block", whiteSpace: "nowrap" }}>
              News Feed
            </Link>
            <Link href="/pipeline" style={{ color: "#d6e7f5", textDecoration: "none", fontSize: "16px", padding: "8px 12px", borderRadius: "8px", display: "block", whiteSpace: "nowrap" }}>
              Pipeline Manager
            </Link>
            <Link href="/settings" style={{ color: "#d6e7f5", textDecoration: "none", fontSize: "16px", padding: "8px 12px", borderRadius: "8px", display: "block", whiteSpace: "nowrap" }}>
              Settings
            </Link>
          </nav>
          
          <CleanupButton />
        </div>
      </aside>
      
      {/* Main Content */}
      <div style={{ flexGrow: 1, overflowY: "auto", display: "flex", flexDirection: "column" }}>
        {/* Toggle Button */}
        <div style={{ padding: "16px", background: "linear-gradient(180deg, #06131d 0%, #0d2131 100%)", display: "flex", alignItems: "center" }}>
          <button 
            onClick={() => setIsOpen(!isOpen)}
            style={{ 
              background: "transparent", 
              border: "none", 
              color: "#fff", 
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "8px"
            }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}