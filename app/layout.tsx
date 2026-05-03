import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "VoteFlow AI - Election Copilot",
  description: "Personalized, process-only election guidance for India."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
