import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Blinkit Flash Analytics Dashboard",
  description: "Discovery Engine Analytics",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
