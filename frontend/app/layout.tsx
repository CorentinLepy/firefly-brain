import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Firefly Brain",
  description: "Dashboard financier personnel compatible Firefly III",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
