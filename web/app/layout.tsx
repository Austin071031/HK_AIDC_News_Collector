import type { ReactNode } from "react";
import Link from "next/link";

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body style={{ margin: 0, display: "flex", minHeight: "100vh", fontFamily: "sans-serif", background: "#f3f7fb" }}>
        {/* Sidebar */}
        <aside style={{ width: "240px", background: "#06131d", color: "#f7fbff", padding: "24px", flexShrink: 0 }}>
          <h2 style={{ fontSize: "18px", color: "#8fd3ff", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "32px" }}>HK AIDC Collector</h2>
          <nav style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <Link href="/" style={{ color: "#d6e7f5", textDecoration: "none", fontSize: "16px", padding: "8px 12px", borderRadius: "8px", display: "block" }}>
              News Feed
            </Link>
            <Link href="/pipeline" style={{ color: "#d6e7f5", textDecoration: "none", fontSize: "16px", padding: "8px 12px", borderRadius: "8px", display: "block" }}>
              Pipeline Manager
            </Link>
          </nav>
        </aside>
        
        {/* Main Content */}
        <div style={{ flexGrow: 1, overflowY: "auto" }}>
          {children}
        </div>
      </body>
    </html>
  );
}
