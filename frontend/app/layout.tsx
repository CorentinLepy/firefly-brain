import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Firefly Brain V2",
  description: "Copilote financier personnel auto-hébergeable compatible Firefly III",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
