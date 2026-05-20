import type { ReactNode } from "react";
import SidebarLayout from "./SidebarLayout";

export const metadata = {
  title: "HK AIDC Collector",
};

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "sans-serif", background: "#f3f7fb" }}>
        <SidebarLayout>
          {children}
        </SidebarLayout>
      </body>
    </html>
  );
}
