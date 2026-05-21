import type { Metadata } from "next";
import { Nav } from "../components/nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lead Gen Agency",
  description: "AI agents that discover, enrich, score, and sell leads.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Nav />
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
