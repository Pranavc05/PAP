import type { Metadata } from "next";
import type { ReactNode } from "react";
import { TopNav } from "../components/nav";
import { AuthProvider } from "../lib/auth";
import "./globals.css";

export const metadata: Metadata = {
  title: "Process Automation AI Academy",
  description: "Learn process automation with interactive workflows and AI coaching."
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <TopNav />
          <main style={{ maxWidth: 960, margin: "24px auto", padding: "0 24px" }}>{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
